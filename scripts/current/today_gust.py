"""
 Generate analysis of Peak Wind Gust
"""
import sys
import numpy

import mx.DateTime
now = mx.DateTime.now()

import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

from iem.plot import MapPlot

# Compute normal from the climate database
sql = """
  select s.id, s.network,
  x(s.geom) as lon, y(s.geom) as lat, 
  case when c.max_sknt > c.max_gust then c.max_sknt else c.max_gust END  as wind
  from summary_%s c, current c2, stations s
  WHERE s.iemid = c.iemid and c2.valid > 'TODAY' and c.day = 'TODAY'
  and c2.iemid = s.iemid
  and (s.network ~* 'ASOS' or s.network = 'AWOS') and s.country = 'US'
  ORDER by lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
icursor.execute( sql)
for row in icursor:
    if row[4] == 0:
        continue
    lats.append( row[3] )
    lons.append( row[2] )
    vals.append( row[4] * 1.16 )
    valmask.append(  (row[1] in ['AWOS','IA_ASOS']) )
    
if len(vals) < 5 or True not in valmask:
    sys.exit(0)

clevs = numpy.arange(0,40,2)
clevs = numpy.append(clevs, numpy.arange(40, 80, 5))
clevs = numpy.append(clevs, numpy.arange(80, 120, 10))

# Iowa
pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
        now.strftime("%Y%m%d%H%M"), )
m = MapPlot(title="Iowa ASOS/AWOS Peak Wind Speed Reports",
            subtitle="%s" % (now.strftime("%d %b %Y"), ),
            pqstr=pqstr, sector='iowa')
m.contourf(lons, lats, vals, clevs, units='MPH')
m.plot_values(lons, lats, vals, '%.0f', valmask=valmask)
m.drawcounties()
m.postprocess(view=False)
