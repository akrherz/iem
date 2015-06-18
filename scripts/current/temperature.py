# Generate current plot of Temperature

import datetime
now = datetime.datetime.now()
from pyiem.plot import MapPlot
import numpy as np
import psycopg2.extras
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)


sql = """
  SELECT s.id as station, s.network, tmpf, drct, sknt,
  ST_x(s.geom) as lon, ST_y(s.geom) as lat
  FROM current c, stations s
  WHERE (s.network ~* 'ASOS' or s.network = 'AWOS') and s.country = 'US' and
  s.state not in ('HI', 'AK') and
  s.iemid = c.iemid and
  (valid + '30 minutes'::interval) > now() and
  tmpf >= -50 and tmpf < 140
"""

lats = []
lons = []
vals = []
valmask = []
icursor.execute(sql)
for row in icursor:
    lats.append(row['lat'])
    lons.append(row['lon'])
    vals.append(row['tmpf'])
    valmask.append((row['network'] in ['AWOS', 'IA_ASOS']))

rng = np.arange(-30, 120, 2)

for sector in ['iowa', 'midwest', 'conus']:
    m = MapPlot(axisbg='white', sector=sector,
                title="%s 2 meter Air Temperature" % (sector.capitalize(), ),
                subtitle=now.strftime("%d %b %Y %-I:%M %p"))
    m.contourf(lons, lats, vals, rng, clevstride=5, units='F')
    m.plot_values(lons, lats, vals, fmt='%.0f')
    if sector == 'iowa':
        m.drawcounties()
    pqstr = ("plot ac %s00 %s_tmpf.png %s_tmpf_%s.png png"
             "") % (datetime.datetime.utcnow().strftime("%Y%m%d%H"),
                    sector, sector, datetime.datetime.utcnow().strftime("%H"))
    m.postprocess(view=False, pqstr=pqstr)
    m.close()
