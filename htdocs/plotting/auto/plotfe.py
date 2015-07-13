#!/usr/bin/env python

import cgi
import memcache
import sys
import os


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
    fmt = form.getfirst('fmt', 'png')[:3]

    mckey = "/plotting/auto/plot/%s/%s.%s" % (p, q, fmt)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if fmt == 'png':
        sys.stdout.write("Content-type: image/png\n\n")
    else:
        sys.stdout.write('Content-type: text/plain\n\n')
    hostname = os.environ.get("SERVER_NAME", "")
    if not res or hostname == "iem.local":
        # Lazy import to help speed things up
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        import cStringIO
        import datetime
        import imp
        name = 'scripts/p%s' % (p,)
        fp, pathname, description = imp.find_module(name)
        a = imp.load_module(name, fp, pathname, description)
        meta = a.get_description()
        response = a.plotter(fdict)
        if not isinstance(response, tuple):
            [fig, df] = [response, None]
        else:
            fig = response[0]
            df = response[1]
        if isinstance(fig, str):
            msg = fig
            fig, ax = plt.subplots(1, 1)
            ax.text(0.5, 0.5, msg, transform=ax.transAxes, ha='center')
        # Place timestamp on the image
        plt.figtext(0.01, 0.01, ('Plot Generated: %s'
                                 ) % (
            datetime.datetime.now().strftime("%-d %b %Y %-I:%M %p"),),
            va='bottom', ha='left', fontsize=10)
        ram = cStringIO.StringIO()
        plt.savefig(ram, format='png', dpi=dpi)
        ram.seek(0)
        res = ram.read()
        sys.stderr.write("Setting cache: %s" % (mckey,))
        if fmt != 'png' and df is not None:
            if fmt == 'csv':
                res = df.to_csv(index=(len(df.columns) == 1))
        mc.set(mckey, res, meta.get('cache', 43200))
    sys.stdout.write(res)

if __name__ == '__main__':
    main()
