# Generate a plot of SDD
import sys
from pyiem.plot import MapPlot

import mx.DateTime
now = mx.DateTime.now()

import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

from pyiem.network import Table as NetworkTable
nt = NetworkTable("IACLIMATE")

# Compute normal from the climate database
sql = """SELECT station,
   sum(sdd86(high, low)) as sdd
   from alldata_ia WHERE year = %s and month = %s
   GROUP by station""" % (now.year, now.month)

lats = []
lons = []
sdd86 = []
valmask = []
ccursor.execute(sql)
for row in ccursor:
    lats.append(nt.sts[row[0]]['lat'])
    lons.append(nt.sts[row[0]]['lon'])
    sdd86.append(float(row[1]))
    valmask.append(True)

if max(sdd86) == 0:
    sys.exit()

m = MapPlot(axisbg='white',
            title="Iowa %s SDD Accumulation" % (now.strftime("%B %Y"), ))
m.contourf(lons, lats, sdd86, range(int(min(sdd86)-1), int(max(sdd86)+1)))
pqstr = "plot c 000000000000 summary/sdd_mon.png bogus png"
m.postprocess(view=False, pqstr=pqstr)
m.close()
