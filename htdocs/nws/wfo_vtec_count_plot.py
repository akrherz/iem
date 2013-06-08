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

def run(phenomena, significance, sts, ets, mc, key):
    """ Figure out what the user wanted and do it! """
    pstr = []
    subtitle = ""
    title = ""
    for p,s in zip(phenomena, significance):
        pstr.append("(phenomena = '%s' and significance = '%s')" % (p,s))
        subtitle += "%s.%s " % (p, s)
        title += "%s %s" % (vtec._phenDict.get(p, p),
                        vtec._sigDict.get(s, s))
    if len(phenomena) > 1:
        title = "VTEC Unique Event"
    pstr = " or ".join( pstr )
    pstr = "(%s)" % (pstr,)

    pcursor.execute("""
with total as (
select distinct wfo, extract(year from issue at time zone 'UTC'), phenomena, 
significance, eventid from warnings 
 where """+ pstr +""" and 
 issue >= '%s 00:00+00' and issue < '%s 00:00+00'
)
SELECT wfo, count(*) from total GROUP by wfo ORDER by count DESC

    """ % (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d")))
    data = {}
    first = True
    for row in pcursor:
        if first:
            if row[1] > 1000:
                global bins
                bins = numpy.array([0,1,5,10,50,100,150,200,250,500,750,1000,1250,1500,2000])
                
            first = False
        data[ row[0]] = row[1]

    p = plot.MapPlot(sector='nws',
                 title='%s Counts by NWS Office' % (title,),
                 subtitle='Valid %s - %s UTC, based on VTEC: %s' % (sts.strftime("%d %b %Y"),
                                                                    ets.strftime("%d %b %Y"),
                                                subtitle))
    p.fill_cwas(data, bins=bins)
    p.postprocess(web=True, memcache=mc, memcachekey=key, memcacheexpire=1800)

if __name__ == '__main__':
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    
    form = cgi.FieldStorage()
    phenomena = []
    phenomena.append( form.getfirst('phenomena', 'TO')[:2] )
    phenomena.append( form.getfirst('phenomena2', ' ')[:2] )
    phenomena.append( form.getfirst('phenomena3', ' ')[:2] )
    phenomena.append( form.getfirst('phenomena4', ' ')[:2] )
    while ' ' in phenomena:
        phenomena.remove(' ')
    significance = []
    significance.append( form.getfirst('significance', 'W')[0] )
    significance.append( form.getfirst('significance2', ' ')[0] )
    significance.append( form.getfirst('significance3', ' ')[0] )
    significance.append( form.getfirst('significance4', ' ')[0] )
    while ' ' in significance:
        significance.remove(' ')
    
    sts = datetime.datetime.strptime(form.getfirst('sts', '20130101'), '%Y%m%d')
    ets = datetime.datetime.strptime(form.getfirst('ets', '20140101'), '%Y%m%d')
    
    key = "wfo_vtec_count_"
    for p,s in zip(phenomena, significance):
        key += "%s.%s_" % (p,s)
    key += "%s_%s.png" % (sts.strftime("%Y%m%d"), ets.strftime("%Y%m%d"))
    res = mc.get(key)
    if res:
        print 'Content-type: image/png\n'
        sys.stdout.write( res )
    else:
        run(phenomena, significance, sts, ets, mc, key)