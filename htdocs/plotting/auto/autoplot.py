"""Our mod_wsgi frontend to autoplot generation"""
# pylint: disable=abstract-class-instantiated
from collections import OrderedDict
import sys
import os
import datetime
import tempfile
import imp
import json
import traceback
from io import BytesIO

import numpy as np
import memcache
import pytz
import pandas as pd
from paste.request import parse_formvars
from six import string_types
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

# Attempt to stop hangs within mod_wsgi and numpy
np.seterr(all="ignore")


HTTP200 = "200 OK"
HTTP400 = "400 Bad Request"
HTTP500 = "500 Internal Server Error"
BASEDIR, WSGI_FILENAME = os.path.split(__file__)
if BASEDIR not in sys.path:
    sys.path.insert(0, BASEDIR)


def format_geojson_response(gdf, defaultcol):
    """Convert geodataframe into GeoJson."""
    # Avert your eyes children
    jdict = json.loads(gdf.to_json(), parse_float=lambda x: round(float(x), 2))
    jdict["meta"] = {}
    jdict["meta"]["propdefault"] = defaultcol
    jdict["meta"]["proporder"] = [x for x in gdf.columns if x != "geom"]
    return json.dumps(jdict)


def parser(cgistr):
    """Convert a CGI string into a dict that gets passed to the plotting
    routine"""
    # want predictable / stable URIs, generally.
    data = OrderedDict()
    for token in cgistr.split("::"):
        token2 = token.split(":")
        if len(token2) != 2:
            continue
        if token2[0] in data:
            if isinstance(data[token2[0]], string_types):
                data[token2[0]] = [data[token2[0]]]
            data[token2[0]].append(token2[1])
        else:
            data[token2[0]] = token2[1]

    return data


def get_response_headers(fmt):
    """Figure out some headers"""
    extra = None
    if fmt == "png":
        ctype = "image/png"
    elif fmt == "js":
        ctype = "application/javascript"
    elif fmt == "geojson":
        ctype = "application/vnd.geo+json"
    elif fmt == "svg":
        ctype = "image/svg+xml"
    elif fmt == "pdf":
        ctype = "application/pdf"
    elif fmt in ["csv", "txt"]:
        ctype = "text/plain"
    else:
        ctype = "application/vnd.ms-excel"
        extra = [("Content-Disposition", "attachment;Filename=iem.xlsx")]
    res = [("Content-type", ctype)]
    if extra:
        res.extend(extra)
    return res


def error_image(message, fmt):
    """Create an error image"""
    plt.close()
    _, ax = plt.subplots(1, 1)
    msg = "IEM Autoplot generation resulted in an error\n%s" % (message,)
    ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha="center", va="center")
    ram = BytesIO()
    plt.axis("off")
    plt.savefig(ram, format=fmt, dpi=100)
    ram.seek(0)
    plt.close()
    return ram.read()


def handle_error(exp, fmt, uri):
    """Handle errors"""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)[-1]
    sys.stderr.write(
        ("URI:%s %s method:%s lineno:%s %s\n")
        % (uri, exp.__class__.__name__, tb[2], tb[1], exp)
    )
    if not isinstance(exp, NoDataFound):
        traceback.print_exc()
    del (exc_type, exc_value, exc_traceback, tb)
    if fmt in ["png", "svg", "pdf"]:
        return error_image(str(exp), fmt)
    elif fmt == "js":
        return "alert('%s');" % (str(exp),)
    return str(exp)


def get_res_by_fmt(p, fmt, fdict):
    """Do the work of actually calling things"""
    if p >= 200:
        name = "scripts200/p%s" % (p,)
    elif p >= 100:
        name = "scripts100/p%s" % (p,)
    else:
        name = "scripts/p%s" % (p,)
    fp, pathname, description = imp.find_module(name)
    a = imp.load_module(name, fp, pathname, description)
    meta = a.get_description()
    # Allow returning of javascript as a string
    if fmt == "js":
        res = a.highcharts(fdict)
    elif fmt == "geojson":
        res = format_geojson_response(*a.geojson(fdict))
    else:
        res = a.plotter(fdict)
    # res should be either a 2 or 3 length tuple, rectify this otherwise
    if not isinstance(res, tuple):
        res = [res, None, None]
    if len(res) == 2:
        res = [res[0], res[1], None]

    return res, meta


def plot_metadata(fig, start_time, end_time, p):
    """Place timestamp on the image"""
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    now = utcnow.astimezone(pytz.timezone("America/Chicago"))
    fig.text(
        0.01,
        0.005,
        ("Generated at %s in %.2fs")
        % (
            now.strftime("%-d %b %Y %-I:%M %p %Z"),
            (end_time - start_time).total_seconds(),
        ),
        va="bottom",
        ha="left",
        fontsize=8,
    )
    fig.text(
        0.99,
        0.005,
        ("IEM Autoplot App #%s") % (p,),
        va="bottom",
        ha="right",
        fontsize=8,
    )


def get_mckey(scriptnum, fdict, fmt):
    """Figure out what our memcache key should be."""
    vals = []
    for key in fdict:
        # Internal app controls should not be used on the memcache key
        if not key.startswith("_"):
            vals.append("%s:%s" % (key, fdict[key]))
    return (
        "/plotting/auto/plot/%s/%s.%s" % (scriptnum, "::".join(vals), fmt)
    ).replace(" ", "")


def workflow(environ, form, fmt):
    """we need to return a status and content"""
    # q is the full query string that was rewritten to use by apache
    q = form.get("q", "")
    fdict = parser(q)
    # p=number is the python backend code called by this framework
    scriptnum = int(form.get("p", 0))
    dpi = int(fdict.get("dpi", 100))

    # memcache keys can not have spaces
    mckey = get_mckey(scriptnum, fdict, fmt)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    if len(mckey) < 250:
        # Don't fetch memcache when we have _cb set for an inbound CGI
        res = mc.get(mckey) if fdict.get("_cb") is None else None
        if res:
            return HTTP200, res
    # memcache failed to save us work, so work we do!
    start_time = datetime.datetime.utcnow()
    # res should be a 3 length tuple
    try:
        res, meta = get_res_by_fmt(scriptnum, fmt, fdict)
    except NoDataFound as exp:
        return HTTP400, handle_error(exp, fmt, environ.get("REQUEST_URI"))
    except Exception as exp:
        # Everything else should be considered fatal
        return HTTP500, handle_error(exp, fmt, environ.get("REQUEST_URI"))
    end_time = datetime.datetime.utcnow()
    sys.stderr.write(
        ("Autoplot[%3s] Timing: %7.3fs Key: %s\n")
        % (scriptnum, (end_time - start_time).total_seconds(), mckey)
    )

    [mixedobj, df, report] = res
    # Our output content
    content = ""
    if fmt == "js" and isinstance(mixedobj, dict):
        content = ('$("#ap_container").highcharts(%s);') % (
            json.dumps(mixedobj),
        )
    elif fmt in ["js", "geojson"]:
        content = mixedobj
    elif fmt in ["svg", "png", "pdf"] and isinstance(mixedobj, plt.Figure):
        # if our content is a figure, then add some fancy metadata to plot
        if meta.get("plotmetadata", True):
            plot_metadata(mixedobj, start_time, end_time, scriptnum)
        ram = BytesIO()
        plt.savefig(ram, format=fmt, dpi=dpi)
        plt.close()
        ram.seek(0)
        content = ram.read()
        del ram
    elif fmt in ["svg", "png", "pdf"] and mixedobj is None:
        return (
            HTTP400,
            error_image(
                ("plot requested but backend " "does not support plots"), fmt
            ),
        )
    elif fmt == "txt" and report is not None:
        content = report
    elif fmt in ["csv", "xlsx"] and df is not None:
        if fmt == "csv":
            content = df.to_csv(index=(df.index.name is not None), header=True)
        elif fmt == "xlsx":
            # Can't write to ram buffer yet, unimplmented upstream
            (_, tmpfn) = tempfile.mkstemp()
            df.index.name = None
            # Need to set engine as xlsx/xls can't be inferred
            with pd.ExcelWriter(tmpfn, engine="openpyxl") as writer:
                df.to_excel(writer, encoding="latin-1", sheet_name="Sheet1")
            content = open(tmpfn, "rb").read()
            os.unlink(tmpfn)
        del df
    else:
        sys.stderr.write(
            ("Undefined edge case: fmt: %s uri: %s\n")
            % (fmt, environ.get("REQUEST_URI"))
        )
        raise Exception("Undefined autoplot action |%s|" % (fmt,))

    try:
        mc.set(mckey, content, meta.get("cache", 43200))
    except Exception as exp:
        sys.stderr.write(
            "Exception while writting key: %s\n%s\n" % (mckey, exp)
        )
    if isinstance(mixedobj, plt.Figure):
        plt.close()
    return HTTP200, content


def application(environ, start_response):
    """Our Application!"""
    # Parse the request that was sent our way
    fields = parse_formvars(environ)
    # HACK
    if fields.get("q", "").find("network:WFO::wfo:PHEB") > -1:
        fields["q"] = fields["q"].replace("network:WFO", "network:NWS")
    if fields.get("q", "").find("network:WFO::wfo:PAAQ") > -1:
        fields["q"] = fields["q"].replace("network:WFO", "network:NWS")
    # Figure out the format that was requested from us, default to png
    fmt = fields.get("fmt", "png")[:7]
    # Figure out what our response headers should be
    response_headers = get_response_headers(fmt)
    try:
        # do the work!
        status, output = workflow(environ, fields, fmt)
    except Exception as exp:
        status = HTTP500
        output = handle_error(exp, fmt, environ.get("REQUEST_URI"))
    start_response(status, response_headers)
    # python3 mod-wsgi requires returning bytes, so we encode strings
    if sys.version_info[0] > 2 and isinstance(output, str):
        output = output.encode("UTF-8")
    return [output]


# from paste.exceptions.errormiddleware import ErrorMiddleware
# application = ErrorMiddleware(application, debug=True)
