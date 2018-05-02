"""Our mod_wsgi frontend to autoplot generation"""
import sys
import os
import datetime
import tempfile
import imp
import traceback
import json
from io import BytesIO, StringIO

import numpy as np
import memcache
import pytz
import pandas as pd
from paste.request import parse_formvars
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
# Attempt to stop hangs within mod_wsgi and numpy
np.seterr(all='ignore')

BASEDIR, WSGI_FILENAME = os.path.split(__file__)
if BASEDIR not in sys.path:
    sys.path.insert(0, BASEDIR)


def parser(cgistr):
    """ Convert a CGI string into a dict that gets passed to the plotting
    routine """
    data = dict()
    for token in cgistr.split("::"):
        token2 = token.split(":")
        if len(token2) != 2:
            continue
        data[token2[0]] = token2[1]

    return data


def get_response_headers(fmt):
    """Figure out some headers"""
    extra = None
    if fmt == 'png':
        ctype = "image/png"
    elif fmt == 'js':
        ctype = "application/javascript"
    elif fmt == 'svg':
        ctype = "image/svg+xml"
    elif fmt == 'pdf':
        ctype = "application/pdf"
    elif fmt in ['csv', 'txt']:
        ctype = 'text/plain'
    else:
        ctype = "application/vnd.ms-excel"
        extra = [("Content-Disposition",  "attachment;Filename=iem.xlsx")]
    res = [('Content-type', ctype)]
    if extra:
        res.extend(extra)
    return res


def handle_error(exp, fmt, uri):
    """Handle an error and provide user something slightly bettter than
    busted image"""
    if isinstance(exp, Exception):
        if isinstance(exp, ValueError):
            sys.stderr.write("[URI:%s] %s\n" % (uri, exp))
        else:
            sys.stderr.write("[URI:%s] Unanticipated Exception\n" % (uri, ))
            traceback.print_exc(file=sys.stderr)
    if fmt in ['png', 'svg', 'pdf']:
        plt.close()
        _, ax = plt.subplots(1, 1)
        msg = "IEM Autoplot generation resulted in an error\n%s" % (str(exp),)
        ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha='center',
                va='center')
        ram = BytesIO()
        plt.axis('off')
        plt.savefig(ram, format=fmt, dpi=100)
        ram.seek(0)
        plt.close()
        return ram.read()
    if isinstance(exp, str):
        return exp
    fh = StringIO()
    traceback.print_exc(file=fh)
    fh.seek(0)
    return fh.read()


def get_res_by_fmt(p, fmt, fdict):
    """Do the work of actually calling things"""
    if p >= 100:
        name = "scripts100/p%s" % (p, )
    else:
        name = 'scripts/p%s' % (p,)
    fp, pathname, description = imp.find_module(name)
    a = imp.load_module(name, fp, pathname, description)
    meta = a.get_description()
    # Allow returning of javascript as a string
    if fmt == 'js':
        res = a.highcharts(fdict)
    else:
        res = a.plotter(fdict)
        # res should be either a 2 or 3 length tuple, rectify this otherwise
        if not isinstance(res, tuple):
            res = [res, None, None]
        else:
            if len(res) == 2:
                res = [res[0], res[1], None]

    return res, meta


def plot_metadata(fig, start_time, end_time, p):
    """Place timestamp on the image"""
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    now = utcnow.astimezone(pytz.timezone("America/Chicago"))
    fig.text(0.01, 0.005, ('Generated at %s in %.2fs'
                           ) % (now.strftime("%-d %b %Y %-I:%M %p %Z"),
                                (end_time - start_time).total_seconds()),
             va='bottom', ha='left', fontsize=8)
    fig.text(0.99, 0.005, ('IEM Autoplot App #%s') % (p, ),
             va='bottom', ha='right', fontsize=8)


def workflow(form, fmt):
    """See how we are called"""
    q = form.get('q', "")
    fdict = parser(q)
    p = int(form.get('p', 0))
    dpi = int(fdict.get('dpi', 100))

    mckey = ("/plotting/auto/plot/%s/%s.%s" % (p, q, fmt)).replace(" ", "")
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    # Don't fetch memcache when we have _cb set for an inbound CGI
    res = mc.get(mckey) if fdict.get('_cb') is None else None
    if res:
        return res
    # do the call please
    start_time = datetime.datetime.utcnow()
    res, meta = get_res_by_fmt(p, fmt, fdict)
    end_time = datetime.datetime.utcnow()
    if fmt == 'js':
        # Legacy support of when the js option returns a dictionary, which
        # we then want to serialize to JSON
        if isinstance(res, dict):
            res = '$("#ap_container").highcharts(%s);' % (json.dumps(res),)
    else:
        [fig, df, report] = res
        # If fig is a string, we hit an error!
        if isinstance(fig, str):
            raise ValueError(fig)
        if fig is not None:
            plot_metadata(fig, start_time, end_time, p)
        ram = BytesIO()
        if fmt in ['png', 'pdf', 'svg']:
            plt.savefig(ram, format=fmt, dpi=dpi)
            ram.seek(0)
            res = ram.read()
        if fmt in ['csv', 'txt', 'xlsx']:
            if df is not None:
                if fmt == 'csv':
                    res = df.to_csv(index=(df.index.name is not None))
                elif fmt == 'xlsx':
                    (_, tmpfn) = tempfile.mkstemp()
                    writer = pd.ExcelWriter(tmpfn, engine='xlsxwriter',
                                            options={'remove_timezone': True})
                    df.index.name = None
                    df.to_excel(writer,
                                encoding='latin-1', sheet_name='Sheet1')
                    writer.close()
                    del writer
                    res = open(tmpfn, 'rb').read()
                    os.unlink(tmpfn)
                del df
            if fmt == 'txt' and report is not None:
                res = report
        plt.close()

    sys.stderr.write(("Autoplot[%3s] Timing: %7.3fs Key: %s\n"
                      ) % (p, (end_time - start_time).total_seconds(), mckey))
    try:
        if not isinstance(res, list):
            mc.set(mckey, res, meta.get('cache', 43200))
    except Exception as exp:
        sys.stderr.write("Exception while writting key: %s\n%s\n" % (mckey,
                                                                     exp))
    return res


def application(environ, start_response):
    """Our Application!"""
    # sys.stderr.write(
    # 'wsgi.multithread = %s\n' % repr(environ['wsgi.multithread']))
    # sys.stderr.write(
    # 'wsgi.progress_group = %s\n' % repr(environ['mod_wsgi.process_group']))
    fields = parse_formvars(environ)
    fmt = fields.get('fmt', 'png')[:4]
    response_headers = get_response_headers(fmt)
    try:
        status = "200 OK"
        output = workflow(fields, fmt)
    except Exception as exp:
        # Lets reserve 500 errors for some unknown server failure
        status = "400 Bad Request"
        output = handle_error(exp, fmt, environ.get('REQUEST_URI'))
    start_response(status, response_headers)
    # sys.stderr.write("OUT: get_fignums() %s\n" % (repr(plt.get_fignums(), )))
    if sys.version_info[0] > 2 and isinstance(output, str):
        output = output.encode('UTF-8')
    return [output]


# from paste.exceptions.errormiddleware import ErrorMiddleware
# application = ErrorMiddleware(application, debug=True)
