"""Our mod_wsgi frontend to autoplot generation"""
# pylint: disable=abstract-class-instantiated
import sys
import os
import tempfile
import importlib.machinery
import importlib.util
import json
import syslog
import traceback
from io import BytesIO

import numpy as np
from pymemcache.client import Client
import pytz
from pandas.api.types import is_datetime64_any_dtype as isdt
import pandas as pd
from PIL import Image
from paste.request import parse_formvars
from six import string_types
from pyiem.util import utc
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

# Attempt to stop hangs within mod_wsgi and numpy
np.seterr(all="ignore")


HTTP200 = "200 OK"
HTTP400 = "400 Bad Request"
HTTP500 = "500 Internal Server Error"
BASEDIR, WSGI_FILENAME = os.path.split(__file__)


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
    data = {}
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
    msg = f"IEM Autoplot generation resulted in an error\n{message}"
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
        f"URI:{uri} {exp.__class__.__name__} "
        f"method:{tb[2]} lineno:{tb[1]} {exp}\n"
    )
    if not isinstance(exp, NoDataFound):
        traceback.print_exc()
    del (exc_type, exc_value, exc_traceback, tb)
    if fmt in ["png", "svg", "pdf"]:
        return error_image(str(exp), fmt)
    if fmt == "js":
        return f"alert('{exp}');"
    return str(exp)


def get_res_by_fmt(p, fmt, fdict):
    """Do the work of actually calling things"""
    suffix = ""
    if p >= 200:
        suffix = "200"
    elif p >= 100:
        suffix = "100"
    fn = f"{BASEDIR}/scripts{suffix}/p{p}.py"
    loader = importlib.machinery.SourceFileLoader(f"p{p}", fn)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)

    meta = mod.get_description()
    # Allow returning of javascript as a string
    if fmt == "js":
        res = mod.highcharts(fdict)
    elif fmt == "geojson":
        res = format_geojson_response(*mod.geojson(fdict))
    else:
        res = mod.plotter(fdict)
    # res should be either a 2 or 3 length tuple, rectify this otherwise
    if not isinstance(res, tuple):
        res = [res, None, None]
    if len(res) == 2:
        res = [res[0], res[1], None]

    return res, meta


def plot_metadata(fig, start_time, p):
    """Place timestamp on the image"""
    now = utc().astimezone(pytz.timezone("America/Chicago"))
    fig.text(
        0.01,
        0.005,
        f"Generated at {now:%-d %b %Y %-I:%M %p %Z} in "
        f"{((utc() - start_time).total_seconds()):.2f}s",
        va="bottom",
        ha="left",
        fontsize=8,
    )
    fig.text(
        0.99,
        0.005,
        f"IEM Autoplot App #{p}",
        va="bottom",
        ha="right",
        fontsize=8,
    )


def get_mckey(scriptnum, fdict, fmt):
    """Figure out what our memcache key should be."""
    vals = []
    for key in fdict:
        # Internal app controls should not be used on the memcache key
        # except when they should be, sigh
        if not key.startswith("_") or key in ["_r"]:
            vals.append(f"{key}:{fdict[key]}")
    return (
        f"/plotting/auto/plot/{scriptnum}/{'::'.join(vals)}.{fmt}"
    ).replace(" ", "")


def workflow(mc, environ, form, fmt):
    """we need to return a status and content"""
    # q is the full query string that was rewritten to use by apache
    q = form.get("q", "")
    fdict = parser(q)
    # p=number is the python backend code called by this framework
    scriptnum = int(form.get("p", 0))
    fdict["dpi"] = min([int(fdict.get("dpi", 100)), 500])

    # memcache keys can not have spaces
    mckey = get_mckey(scriptnum, fdict, fmt)
    if len(mckey) < 250:
        # Don't fetch memcache when we have _cb set for an inbound CGI
        res = mc.get(mckey) if fdict.get("_cb") is None else None
        if res:
            return HTTP200, res
    # memcache failed to save us work, so work we do!
    start_time = utc()
    # res should be a 3 length tuple
    try:
        res, meta = get_res_by_fmt(scriptnum, fmt, fdict)
    except NoDataFound as exp:
        return HTTP400, handle_error(exp, fmt, environ.get("REQUEST_URI"))
    except Exception as exp:
        # Everything else should be considered fatal
        return HTTP500, handle_error(exp, fmt, environ.get("REQUEST_URI"))

    [mixedobj, df, report] = res
    # Our output content
    content = ""
    if fmt == "js" and isinstance(mixedobj, dict):
        content = f'$("#ap_container").highcharts({json.dumps(mixedobj)});'
    elif fmt in ["js", "geojson"]:
        content = mixedobj
    elif fmt in ["svg", "png", "pdf"]:
        if isinstance(mixedobj, plt.Figure):
            # if our content is a figure, then add some fancy metadata to plot
            if meta.get("plotmetadata", True):
                plot_metadata(mixedobj, start_time, scriptnum)
            ram = BytesIO()
            plt.savefig(ram, format=fmt, dpi=fdict["dpi"])
            plt.close()
            ram.seek(0)
            content = ram.read()
            del ram
        elif isinstance(mixedobj, Image.Image):
            ram = BytesIO()
            mixedobj.save(ram, fmt)
            ram.seek(0)
            content = ram.read()
            del ram

        elif mixedobj is None:
            return (
                HTTP400,
                error_image(
                    ("plot requested but backend does not support plots"), fmt
                ),
            )
    elif fmt == "txt" and report is not None:
        content = report
    elif fmt in ["csv", "xlsx"] and df is not None:
        # Dragons: do timestamp conversion as pandas has many bugs
        for column in df.columns:
            if isdt(df[column]):
                df[column] = df[column].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        if fmt == "csv":
            content = df.to_csv(index=(df.index.name is not None), header=True)
        elif fmt == "xlsx":
            # Can't write to ram buffer yet, unimplmented upstream
            (_, tmpfn) = tempfile.mkstemp()
            df.index.name = None
            # Need to set engine as xlsx/xls can't be inferred
            with pd.ExcelWriter(tmpfn, engine="openpyxl") as writer:
                df.to_excel(writer, encoding="latin-1", sheet_name="Sheet1")
            with open(tmpfn, "rb") as fh:
                content = fh.read()
            os.unlink(tmpfn)
        del df
    else:
        sys.stderr.write(
            f"Undefined edge case: fmt: {fmt} "
            f"uri: {environ.get('REQUEST_URI')}\n"
        )
        raise Exception(f"Undefined autoplot action |{fmt}|")

    dur = int(meta.get("cache", 43200))
    try:
        # we have a 10 MB limit within memcache, so don't write objects bigger
        if len(content) < 9.5 * 1024 * 1024:
            # Default encoding is ascii for text
            mc.set(
                mckey,
                (
                    content
                    if isinstance(content, bytes)
                    else content.encode("utf-8")
                ),
                dur,
            )
        else:
            sys.stderr.write(
                f"Memcache object too large: {len(content)} "
                f"uri: {environ.get('REQUEST_URI')}\n"
            )
    except Exception as exp:
        sys.stderr.write(f"Exception while writting key: {mckey}\n{exp}\n")
    if isinstance(mixedobj, plt.Figure):
        plt.close()
    syslog.syslog(
        syslog.LOG_LOCAL1 | syslog.LOG_INFO,
        f"Autoplot[{scriptnum:3.0f}] "
        f"Timing: {(utc() - start_time).total_seconds():.3f}s "
        f"Key: {mckey} Cache: {dur}[s]",
    )
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
    mc = Client(["iem-memcached", 11211])
    try:
        # do the work!
        status, output = workflow(mc, environ, fields, fmt)
    except Exception as exp:
        status = HTTP500
        output = handle_error(exp, fmt, environ.get("REQUEST_URI"))
    finally:
        mc.close()
    start_response(status, response_headers)
    # python3 mod-wsgi requires returning bytes, so we encode strings
    if sys.version_info[0] > 2 and isinstance(output, str):
        output = output.encode("UTF-8")
    return [output]


# from paste.exceptions.errormiddleware import ErrorMiddleware
# application = ErrorMiddleware(application, debug=True)
