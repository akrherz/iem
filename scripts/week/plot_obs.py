"""
 Generate analysis of precipitation
"""

import random
from pyiem.plot import MapPlot

import datetime
now = datetime.datetime.now()

import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
select s.id, 
  ST_x(s.geom) as lon, ST_y(s.geom) as lat, 
  sum(pday) as rainfall
 from summary_%s c, stations s
 WHERE day > ('TODAY'::date - '7 days'::interval) 
 and s.network in ('AWOS', 'IA_ASOS')
 and pday >= 0 and pday < 30 and 
 s.iemid = c.iemid
 GROUP by s.id, lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
icursor.execute(sql)
for row in icursor:
    lats.append( row[2] )
    lons.append( row[1] + (random.random() * 0.01))
    vals.append( row[3] )
    valmask.append( True )

m = MapPlot(
        title='Iowa Past Seven Days Precipitation',
        subtitle="%s - %s inclusive" % (
            (now - datetime.timedelta(days=6)).strftime("%d %b %Y"), 
            now.strftime("%d %b %Y") )
        )
m.plot_values(lons, lats, vals, '%.2f')
m.drawcounties()
pqstr = "plot c 000000000000 summary/7day/ia_precip.png bogus png"
m.postprocess(pqstr=pqstr)
