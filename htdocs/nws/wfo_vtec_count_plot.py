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
bins = numpy.array([0,1,3,5,10,20,35,50,75,100,150,200,250,500,750,1000])

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

def run(phenomena, significance, year, mc, key):
    """ Figure out what the user wanted and do it! """

    pcursor.execute("""
with total as (
select distinct wfo, eventid from warnings_"""+`year`+""" 
 where phenomena = %s and significance = %s
)
SELECT wfo, count(*) from total GROUP by wfo

    """, (phenomena, significance))
    data = {}
    for row in pcursor:
        data[ row[0]] = row[1]

    p = plot.MapPlot(sector='nws',
                 title='%s %s %s Counts by NWS Office' % (year,
                        vtec._phenDict.get(phenomena, phenomena),
                        vtec._sigDict.get(significance, significance)),
                 subtitle='Valid %s, based on VTEC: %s.%s' % (utc.strftime("%d %b %Y %H%M UTC"),
                                                phenomena, significance))
    p.fill_cwas(data, bins=bins)
    p.postprocess(web=True, memcache=mc, memcachekey=key, memcacheexpire=1800)

if __name__ == '__main__':
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    
    form = cgi.FieldStorage()
    phenomena = form.getfirst('phenomena', 'TO')[:2]
    significance = form.getfirst('significance', 'W')[0]
    year = int(form.getfirst('year', 2013))
    key = "wfo_vtec_count_%s_%s_%s.png" % (year, phenomena, significance)
    res = mc.get(key)
    if res:
        print 'Content-type: image/png\n'
        sys.stdout.write( res )
    else:
        run(phenomena, significance, year, mc, key)