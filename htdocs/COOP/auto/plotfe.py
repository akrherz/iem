#!/usr/bin/env python

import cgi
import cStringIO
import sys
import imp
import memcache
import datetime
import matplotlib.pyplot as plt

def parser(cgistr):
    """ Convert a CGI string into a dict that gets passed to the plotting 
    routine """
    d = dict()
    for token in cgistr.split("_"):
        token2 = token.split(":")
        if len(token2) != 2:
            continue
        d[token2[0]] = token2[1]
    
    return d

if __name__ == '__main__':
    form = cgi.FieldStorage()
    q = form.getfirst('q', "")
    fdict = parser( q )
    p = int(form.getfirst('p', 0))
    dpi = int(fdict.get('dpi', 100))

    mckey = "/COOP/auto/plot/%s/%s.png" % (p, q)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    sys.stdout.write("Content-type: image/png\n\n")
    if not res:
        name = 'scripts/p%s' % (p,)
        fp, pathname, description = imp.find_module(name)
        a = imp.load_module(name, fp, pathname, description)
        fig = a.plotter(fdict)
        # Place timestamp on the image
        fig.text(0.01, 0.01, 'Plot Generated: %s' % (
                datetime.datetime.now().strftime("%-d %b %Y %-I:%M %p"),), 
                 va='bottom', ha='left', fontsize=10)
        ram = cStringIO.StringIO()
        plt.savefig(ram, format='png', dpi=dpi)
        ram.seek(0)
        res = ram.read()
        mc.set(mckey, res, 86400)
    sys.stdout.write( res )
