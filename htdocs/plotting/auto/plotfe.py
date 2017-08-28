#!/usr/bin/env python
"""The Autoplot frontend that does a complex number of things"""

import sys
import os
import cgi
import datetime
import tempfile
import imp
import traceback
import json
import cStringIO

import memcache
import pandas as pd
import pytz


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


def send_content_type(fmt):
    """Send the content-type header for this fmt"""
    if fmt == 'png':
        sys.stdout.write("Content-type: image/png\n\n")
    elif fmt == 'js':
        sys.stdout.write("Content-type: application/javascript\n\n")
    elif fmt == 'svg':
        sys.stdout.write("Content-type: image/svg+xml\n\n")
    elif fmt == 'pdf':
        sys.stdout.write("Content-type: application/pdf\n\n")
    elif fmt in ['csv', 'txt']:
        sys.stdout.write('Content-type: text/plain\n\n')
    else:
        sys.stdout.write("Content-type: application/vnd.ms-excel\n")
        sys.stdout.write((
            "Content-Disposition: attachment;Filename=iem.xlsx\n\n"))


def handle_error(exp, fmt):
    """Handle an error and provide user something slightly bettter than
    busted image"""
    sys.stdout.write("Status: 500\n")
    send_content_type(fmt)
    if fmt in ['png', 'svg', 'pdf']:
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        _, ax = plt.subplots(1, 1)
        ax.text(0.5, 0.5, str(exp), transform=ax.transAxes, ha='center')
        ram = cStringIO.StringIO()
        plt.savefig(ram, format=fmt, dpi=100)
        ram.seek(0)
        sys.stdout.write(ram.read())
    else:
        if isinstance(exp, str):
            sys.stdout.write(exp)
        else:
            traceback.print_exc(file=sys.stdout)
    if isinstance(exp, Exception):
        traceback.print_exc(file=sys.stderr)
    sys.exit()


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


def plot_metadata(plt, start_time, end_time, p):
    """Place timestamp on the image"""
    utcnow = datetime.datetime.utcnow(
                                    ).replace(tzinfo=pytz.timezone("UTC"))
    now = utcnow.astimezone(pytz.timezone("America/Chicago"))
    plt.figtext(0.01, 0.005, ('Generated at %s in %.2fs'
                              ) % (now.strftime("%-d %b %Y %-I:%M %p %Z"),
                                   (end_time - start_time).total_seconds()
                                   ),
                va='bottom', ha='left', fontsize=8)
    plt.figtext(0.99, 0.005, ('IEM Autoplot App #%s'
                              ) % (p, ),
                va='bottom', ha='right', fontsize=8)


def do(form, fmt):
    """See how we are called"""
    q = form.getfirst('q', "")
    fdict = parser(q)
    p = int(form.getfirst('p', 0))
    dpi = int(fdict.get('dpi', 100))

    mckey = ("/plotting/auto/plot/%s/%s.%s" % (p, q, fmt)).replace(" ", "")
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    # Don't fetch memcache when we have _cb set for an inbound CGI
    res = mc.get(mckey) if fdict.get('_cb') is None else None
    if res:
        send_content_type(fmt)
        sys.stdout.write(res)
        return
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
        # Lazy import to help speed things up
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        [fig, df, report] = res
        # If fig is a string, we hit an error!
        if isinstance(fig, str):
            handle_error(fig, fmt)
        plot_metadata(plt, start_time, end_time, p)
        ram = cStringIO.StringIO()
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
                    res = open(tmpfn, 'rb').read()
                    os.unlink(tmpfn)
            if fmt == 'txt' and report is not None:
                res = report

    sys.stderr.write(("Autoplot[%3s] Timing: %7.3fs Key: %s\n"
                      ) % (p, (end_time - start_time).total_seconds(), mckey))
    try:
        mc.set(mckey, res, meta.get('cache', 43200))
    except Exception as _:
        sys.stderr.write("Exception while writting key: %s\n" % (mckey, ))
    send_content_type(fmt)
    sys.stdout.write(res)


def main():
    form = cgi.FieldStorage()
    fmt = form.getfirst('fmt', 'png')[:4]
    try:
        do(form, fmt)
    except Exception as exp:
        handle_error(exp, fmt)


if __name__ == '__main__':
    main()
