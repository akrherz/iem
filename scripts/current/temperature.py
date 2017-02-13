# Generate current plot of Temperature

import datetime
from pyiem.plot import MapPlot
from pandas.io.sql import read_sql
import psycopg2
# contour.py:370: RuntimeWarning: invalid value encountered in true_divide
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
now = datetime.datetime.now()
pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')

df = read_sql("""
  SELECT s.id as station, s.network, tmpf, drct, sknt,
  ST_x(s.geom) as lon, ST_y(s.geom) as lat
  FROM current c, stations s
  WHERE (s.network ~* 'ASOS' or s.network = 'AWOS') and s.country = 'US' and
  s.state not in ('HI', 'AK') and
  s.iemid = c.iemid and
  (valid + '30 minutes'::interval) > now() and
  tmpf >= -50 and tmpf < 140
""", pgconn, index_col='station')

rng = np.arange(-30, 120, 2)

for sector in ['iowa', 'midwest', 'conus']:
    m = MapPlot(axisbg='white', sector=sector,
                title="%s 2 meter Air Temperature" % (sector.capitalize(), ),
                subtitle=now.strftime("%d %b %Y %-I:%M %p"))
    m.contourf(df['lon'].values, df['lat'].values, df['tmpf'].values,
               rng, clevstride=5, units='F')
    m.plot_values(df['lon'].values, df['lat'].values, df['tmpf'].values,
                  fmt='%.0f')
    if sector == 'iowa':
        m.drawcounties()
    pqstr = ("plot ac %s00 %s_tmpf.png %s_tmpf_%s.png png"
             "") % (datetime.datetime.utcnow().strftime("%Y%m%d%H"),
                    sector, sector, datetime.datetime.utcnow().strftime("%H"))
    m.postprocess(view=False, pqstr=pqstr)
    m.close()
