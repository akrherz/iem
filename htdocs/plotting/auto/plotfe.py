#!/usr/bin/env python

import cgi
import memcache
import sys
import os
import datetime
import pandas as pd
import tempfile
import imp
        

def parser(cgistr):
    """ Convert a CGI string into a dict that gets passed to the plotting
    routine """
    d = dict()
    for token in cgistr.split("::"):
        token2 = token.split(":")
        if len(token2) != 2:
            continue
        d[token2[0]] = token2[1]

    return d


def main():
    """See how we are called"""
    form = cgi.FieldStorage()
    q = form.getfirst('q', "")
    fdict = parser(q)
    p = int(form.getfirst('p', 0))
    dpi = int(fdict.get('dpi', 100))
    fmt = form.getfirst('fmt', 'png')[:4]

    mckey = ("/plotting/auto/plot/%s/%s.%s" % (p, q, fmt)).replace(" ", "")
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if fmt == 'png':
        sys.stdout.write("Content-type: image/png\n\n")
    elif fmt == 'js':
        sys.stdout.write("Content-type: application/javascript\n\n")
    elif fmt in ['csv', 'txt']:
        sys.stdout.write('Content-type: text/plain\n\n')
    else:
        sys.stdout.write("Content-type: application/vnd.ms-excel\n")
        sys.stdout.write((
            "Content-Disposition: attachment;Filename=iem.xlsx\n\n"))
    hostname = os.environ.get("SERVER_NAME", "")
    if not res and fmt == 'js':
        import json
        # We can short circuit things
        if p >= 100:
            name = "scripts100/p%s" % (p, )
        else:
            name = 'scripts/p%s' % (p,)
        fp, pathname, description = imp.find_module(name)
        a = imp.load_module(name, fp, pathname, description)
        res = '$("#ap_container").highcharts(%s);' % (
                json.dumps(a.highcharts(fdict)), )
    elif not res or hostname == "iem.local":
        # Lazy import to help speed things up
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        import cStringIO
        if p >= 100:
            name = "scripts100/p%s" % (p, )
        else:
            name = 'scripts/p%s' % (p,)
        start_time = datetime.datetime.now()
        fp, pathname, description = imp.find_module(name)
        a = imp.load_module(name, fp, pathname, description)
        meta = a.get_description()
        response = a.plotter(fdict)
        if not isinstance(response, tuple):
            [fig, df, report] = [response, None, None]
        else:
            fig = response[0]
            df = response[1]
            if len(response) == 3:
                report = response[2]
            else:
                report = None
        if isinstance(fig, str):
            msg = fig
            fig, ax = plt.subplots(1, 1)
            ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha='center')
        end_time = datetime.datetime.now()
        # Place timestamp on the image
        plt.figtext(0.01, 0.005, ('Plot Generated at %s in %.2fs'
                                  ) % (
            datetime.datetime.now().strftime("%-d %b %Y %-I:%M %p"),
            (end_time - start_time).total_seconds()),
            va='bottom', ha='left', fontsize=8)
        ram = cStringIO.StringIO()
        plt.savefig(ram, format='png', dpi=dpi)
        ram.seek(0)
        res = ram.read()
        sys.stderr.write("Setting cache: %s" % (mckey,))
        if fmt != 'png':
            if df is not None:
                if fmt == 'csv':
                    res = df.to_csv()
                elif fmt == 'xlsx':
                    (_, tmpfn) = tempfile.mkstemp()
                    writer = pd.ExcelWriter(tmpfn, engine='xlsxwriter')
                    df.index.name = None
                    df.to_excel(writer,
                                encoding='latin-1', sheet_name='Sheet1')
                    writer.close()
                    res = open(tmpfn, 'rb').read()
                    os.unlink(tmpfn)
            if fmt == 'txt' and report is not None:
                sys.stdout.write(report)
                return
        try:
            mc.set(mckey, res, meta.get('cache', 43200))
        except:
            sys.stderr.write("Exception while writting key: %s" % (mckey, ))
    sys.stdout.write(res)

if __name__ == '__main__':
    main()
