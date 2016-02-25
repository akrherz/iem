# Output the 12z morning low temperature
import sys
import matplotlib.cm as cm
import numpy as np
import datetime
from pyiem.plot import MapPlot
import psycopg2
from pyiem.tracker import loadqc

now = datetime.datetime.now()
qdict = loadqc()
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

sql = """
  select s.id,
  ST_x(s.geom) as lon, ST_y(s.geom) as lat,
  max_tmpf as high, s.network
  from summary c, stations s
  WHERE c.iemid = s.iemid and day = 'TODAY' and max_tmpf > -40
  and s.network in ('IA_ASOS', 'AWOS', 'IL_ASOS','MO_ASOS','KS_ASOS',
  'NE_ASOS','SD_ASOS','MN_ASOS','WI_ASOS') ORDER by high ASC
"""

lats = []
lons = []
vals = []
valmask = []
labels = []
icursor.execute(sql)
dsm = None
for row in icursor:
    if row[0] == 'DSM':
        dsm = row[3]
    if qdict.get(row[0], {}).get('tmpf') is not None:
        continue
    lats.append(row[2])
    lons.append(row[1])
    vals.append(row[3])
    labels.append(row[0])
    valmask.append(row[4] in ['AWOS', 'IA_ASOS'])

if len(lats) < 4:
    sys.exit()

m = MapPlot(sector='iowa',
            title=("%s Iowa ASOS/AWOS High Temperature"
                   "") % (now.strftime("%-d %b %Y"),),
            subtitle='map valid: %s' % (now.strftime("%d %b %Y %-I:%M %p"), ))
# m.debug = True
if dsm is None:
    dsm = vals[0]

bottom = int(dsm) - 15
top = int(dsm) + 15
bins = np.linspace(bottom, top, 11)
cmap = cm.get_cmap('jet')
m.contourf(lons, lats, vals, bins, units='F', cmap=cmap)
m.plot_values(lons, lats, vals, '%.0f', valmask=valmask, labels=labels,
              labelbuffer=10)
m.drawcounties()

pqstr = "plot ac %s summary/iowa_asos_high.png iowa_asos_high.png png" % (
        now.strftime("%Y%m%d%H%M"), )

m.postprocess(pqstr=pqstr)
m.close()
