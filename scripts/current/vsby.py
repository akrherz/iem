"""Generate current plot of visibility"""
from pyiem.plot import MapPlot
import sys
import datetime
import psycopg2
import numpy as np
import matplotlib.cm as cm

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = IEM.cursor()

# Compute normal from the climate database
sql = """
SELECT
  id, network, vsby, ST_x(geom) as lon, ST_y(geom) as lat
FROM
  current c JOIN stations s ON (s.iemid = c.iemid)
WHERE
  s.network IN ('AWOS', 'IA_ASOS','IL_ASOS','MN_ASOS','WI_ASOS','SD_ASOS',
              'NE_ASOS','MO_ASOS') and
  valid + '60 minutes'::interval > now() and
  vsby >= 0 and vsby <= 10
"""

lats = []
lons = []
vals = []
valmask = []
cursor.execute(sql)
for row in cursor:
    lats.append(row[4])
    lons.append(row[3])
    vals.append(row[2])
    valmask.append(row[1] in ['AWOS', 'IA_ASOS'])

if len(lats) < 5:
    sys.exit(0)

now = datetime.datetime.now()

m = MapPlot(sector='iowa',
            title='Iowa Visibility',
            subtitle='Valid: %s' % (now.strftime("%d %b %Y %-I:%M %p"),))

m.contourf(lons, lats, vals, np.array([0.01, 0.1, 0.25, 0.5, 1, 2, 3,
                                       5, 8, 9.9]),
           units='miles', cmap=cm.get_cmap('gray'))

m.plot_values(lons, lats, vals, '%.1f', valmask)
m.drawcounties()

pqstr = ("plot ac %s00 iowa_vsby.png vsby_contour_%s00.png png"
         "") % (datetime.datetime.utcnow().strftime("%Y%m%d%H"),
                datetime.datetime.utcnow().strftime("%H"))
m.postprocess(pqstr=pqstr)
m.close()
