# Plot the COOP Precipitation Reports, don't use lame-o x100

from pyiem.plot import MapPlot
import datetime

import psycopg2.extras
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)

sql = """
select id,
  ST_x(s.geom) as lon, ST_y(s.geom) as lat,
  pday
from summary c, stations s
WHERE day = 'TODAY' and pday >= 0 and pday < 20
and s.network = 'IA_COOP' and s.iemid = c.iemid
"""


def n(val):
    if val == 0.0001:
        return 'T'
    if val == 0:
        return '0'
    return '%.2f' % (val,)

lats = []
lons = []
vals = []
valmask = []
labels = []
icursor.execute(sql)
for row in icursor:
    lats.append(row['lat'])
    lons.append(row['lon'])
    vals.append(n(row['pday']))
    labels.append(row['id'])
    valmask.append(True)

m = MapPlot(title="Iowa COOP 24 Hour Precipitation", axisbg='white',
            subtitle="ending approximately %s 7 AM" % (
                            datetime.datetime.now().strftime("%-d %b %Y"), ))
m.plot_values(lons, lats, vals)
pqstr = "plot ac %s iowa_coop_precip.png iowa_coop_precip.png png" % (
        datetime.datetime.now().strftime("%Y%m%d%H%M"), )
m.postprocess(pqstr=pqstr)
