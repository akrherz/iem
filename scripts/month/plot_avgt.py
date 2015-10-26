""" Plot the average temperature for the month"""
from pyiem.plot import MapPlot
import datetime
import sys
import numpy as np
import psycopg2.extras
now = datetime.datetime.now()
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Compute normal from the climate database
sql = """SELECT id, s.network, ST_x(s.geom) as lon, ST_y(s.geom) as lat,
    avg( (max_tmpf + min_tmpf)/2.0 ) as avgt , count(*) as cnt
    from summary_%s c JOIN stations s ON (s.iemid = c.iemid)
    WHERE (s.network ~* 'ASOS' or s.network = 'AWOS') and
    s.country = 'US' and
    extract(month from day) = extract(month from now())
    and max_tmpf > -30 and min_tmpf < 90 GROUP by id, s.network, lon, lat
""" % (now.year,)

lats = []
lons = []
vals = []
valmask = []
icursor.execute(sql)
for row in icursor:
    if row['cnt'] != now.day:
        continue
    lats.append(row['lat'])
    lons.append(row['lon'])
    vals.append(row['avgt'])
    valmask.append(row['network'] in ['AWOS', 'IA_ASOS'])

if len(vals) < 3:
    sys.exit()

m = MapPlot(axisbg='white',
            title="Iowa %s Average Temperature" % (now.strftime("%Y %B"),),
            subtitle=("Average of the High + Low ending: %s"
                      "") % (now.strftime("%d %B"), ))
m.contourf(lons, lats, vals, np.linspace(int(min(vals)), int(max(vals)) + 3,
                                         10))
pqstr = "plot c 000000000000 summary/mon_mean_T.png bogus png"
m.postprocess(view=False, pqstr=pqstr)
m.close()
