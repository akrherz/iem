"""
 Generate analysis of Peak Wind Gust
"""
import sys
import numpy

import datetime
import psycopg2
from pyiem.plot import MapPlot
from pyiem.datatypes import speed

now = datetime.datetime.now()
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

# Compute normal from the climate database
sql = """
  select s.id, s.network,
  ST_x(s.geom) as lon, ST_y(s.geom) as lat,
  greatest(c.max_sknt, c.max_gust) as wind
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
icursor.execute(sql)
for row in icursor:
    if row[4] == 0 or row[4] is None:
        continue
    lats.append(row[3])
    lons.append(row[2])
    vals.append(speed(row[4], 'KT').value('MPH'))
    valmask.append((row[1] in ['AWOS', 'IA_ASOS']))

if len(vals) < 5 or True not in valmask:
    sys.exit(0)

clevs = numpy.arange(0, 40, 2)
clevs = numpy.append(clevs, numpy.arange(40, 80, 5))
clevs = numpy.append(clevs, numpy.arange(80, 120, 10))

# Iowa
pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
        now.strftime("%Y%m%d%H%M"), )
m = MapPlot(title="Iowa ASOS/AWOS Peak Wind Speed Reports",
            subtitle="%s" % (now.strftime("%d %b %Y"), ),
            sector='iowa')
m.contourf(lons, lats, vals, clevs, units='MPH')
m.plot_values(lons, lats, vals, '%.0f', valmask=valmask,
              labelbuffer=10)
m.drawcounties()
m.postprocess(pqstr=pqstr, view=False)
m.close()
