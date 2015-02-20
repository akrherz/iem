# Generate a plot of GDD for the ASOS/AWOS network
from pyiem.plot import MapPlot
import sys
import datetime
now = datetime.datetime.now() - datetime.timedelta(days=1)
import numpy as np
from pyiem.network import Table as NetworkTable
st = NetworkTable('IACLIMATE')
import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()


gfunc = "gdd50"
gbase = 50
if len(sys.argv) == 2 and sys.argv[1] == "gdd52":
    gfunc = "gdd52"
    gbase = 52
if len(sys.argv) == 2 and sys.argv[1] == "gdd48":
    gfunc = "gdd48"
    gbase = 48

# Compute normal from the climate database
ccursor.execute("""SELECT station,
   sum(%s(high, low)) as gdd
   from alldata_ia WHERE station != 'IA0000' and year = %s
   GROUP by station""" % (gfunc, now.year))

lats = []
lons = []
gdd50 = []
valmask = []

for row in ccursor:
    station = row[0]
    if station not in st.sts:
        continue
    lats.append(st.sts[station]['lat'])
    lons.append(st.sts[station]['lon'])
    gdd50.append(float(row[1]))
    valmask.append(True)

m = MapPlot(axisbg='white',
            title="Iowa %s GDD (base=%s) Accumulation" % (now.strftime("%Y"),
                                                          gbase),
            subtitle="1 Jan - %s" % (now.strftime("%d %b %Y"), ))
minval = min(gdd50)
rng = max([int(max(gdd50) - minval), 10])
m.contourf(lons, lats, gdd50, np.linspace(minval, minval+rng, 10))
pqstr = "plot c 000000000000 summary/gdd_jan1.png bogus png"
if gbase == 52:
    pqstr = "plot c 000000000000 summary/gdd52_jan1.png bogus png"
elif gbase == 48:
    pqstr = "plot c 000000000000 summary/gdd48_jan1.png bogus png"
m.postprocess(view=False, pqstr=pqstr)
m.close()
