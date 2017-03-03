from pyiem.plot import MapPlot
import datetime
import numpy as np
import psycopg2
from pyiem.network import Table as NetworkTable
st = NetworkTable('IACLIMATE')
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

ts = datetime.datetime.now() - datetime.timedelta(days=1)

nrain = []
lats = []
lons = []

# Get normals!
ccursor.execute("""
 WITH yearly as (
   SELECT station, year, sum(snow) from alldata_ia WHERE snow > 0
   GROUP by station, year)

    SELECT station, avg(sum) as acc, min(year), max(year) from yearly
    GROUP by station
    ORDER by acc ASC""")
for row in ccursor:
    if row[1] < 20:
        continue
    print("%s %4.1f %i %i" % row)
    station = row[0]
    if station not in st.sts:
        continue
    nrain.append(row[1])
    lats.append(st.sts[station]['lat'])
    lons.append(st.sts[station]['lon'])

m = MapPlot(axisbg='white',
            title="Iowa Seasonal Snowfall Total (inch)")
rng = np.arange(int(min(nrain))-1, int(max(nrain))+1, 2)
m.contourf(lons, lats, nrain, rng, units='inch')
m.plot_values(lons, lats, nrain, fmt='%.1f')
m.drawcounties()
m.postprocess(filename='test.png')
m.close()
