#!/usr/bin/env python

import sys
import numpy
from pyiem import plot
from pyiem.nws import vtec
import psycopg2
import cgi
import datetime
import memcache
    
utc = datetime.datetime.utcnow()
bins = numpy.array([0,1,14,31,91,182,273,365,730,1460,2920,3800])

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

def run(phenomena, significance, mc, key):
    """ Figure out what the user wanted and do it! """

    pcursor.execute("""
 select wfo,  extract(days from ('TODAY'::date - max(issue))) as m from warnings 
 where significance = %s and phenomena = %s GROUP by wfo ORDER by m ASC
    """, (significance, phenomena))
    data = {}
    for row in pcursor:
        data[ row[0]] = max([row[1],0])

    p = plot.MapPlot(sector='conus',
                 title='Days since Last %s %s by NWS Office' % (
                        vtec._phenDict.get(phenomena, phenomena),
                        vtec._sigDict.get(significance, significance)),
                 subtitle='Valid %s' % (utc.strftime("%d %b %Y %H%M UTC"),))
    p.fill_cwas(data, bins=bins)
    p.postprocess(web=True, memcache=mc, memcachekey=key, memcacheexpire=1800)

if __name__ == '__main__':
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    
    form = cgi.FieldStorage()
    phenomena = form.getfirst('phenomena', 'TO')[:2]
    significance = form.getfirst('significance', 'W')[0]
    key = "days_since_%s_%s.png" % (phenomena, significance)
    res = mc.get(key)
    if res:
        print 'Content-type: image/png\n'
        sys.stdout.write( res )
    else:
        run(phenomena, significance, mc, key)