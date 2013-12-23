"""
 Generate a plot of NWS COOP precip reports
"""
from pyiem.plot import MapPlot
import datetime
now = datetime.datetime.now()

import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
SELECT 
  id, s.network, pday, ST_x(s.geom) as lon, ST_y(s.geom) as lat
FROM 
  current c, stations s
WHERE
  c.iemid = s.iemid and 
  s.network IN ('IA_COOP') and
  valid > 'TODAY' and pday >= 0
"""

lats = []
lons = []
vals = []
icursor.execute( sql )
for row in icursor:
    lats.append( row[4] )
    lons.append( row[3] )
    val = row[2]
    if val > 0:
        vals.append("%.2f" % (val,) )
    else:
        vals.append("0")

m = MapPlot(sector='iowa',
            title='NWS COOP 24 Hour Precipitation',
            subtitle="%s 7 AM" % (now.strftime("%d %b %Y"),))

m.plot_values(lons,lats, vals, '%s')
pqstr = "plot c 000000000000 iowa_coop_precip.png bogus png"
m.postprocess(pqstr=pqstr)
m.close()
