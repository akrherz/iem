"""Generate a plot of GDD"""

from pyiem.plot import MapPlot
import numpy as np
import datetime
import psycopg2
from pyiem.network import Table as NetworkTable
import sys

now = datetime.datetime.now()
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

nt = NetworkTable("IACLIMATE")


# Compute normal from the climate database
sql = """SELECT station,
   sum(gdd50(high, low)) as gdd
   from alldata_ia WHERE year = %s and month = %s
   GROUP by station""" % (now.year, now.month)

vals = []
lats = []
lons = []
ccursor.execute(sql)
for row in ccursor:
    if row[0] not in nt.sts:
        continue
    lats.append(nt.sts[row[0]]['lat'])
    lons.append(nt.sts[row[0]]['lon'])
    vals.append(float(row[1]))

if len(vals) < 5:
    sys.exit()

m = MapPlot(title="Iowa %s GDD Accumulation" % (now.strftime("%B %Y"), ),
            axisbg='white')
m.contourf(lons, lats, vals, np.linspace(int(min(vals)), int(max(vals))+3, 10),
           units='base 50')
m.plot_values(lons, lats, vals, fmt='%.0f')

pqstr = "plot c 000000000000 summary/gdd_mon.png bogus png"
m.postprocess(view=False, pqstr=pqstr)
m.close()
