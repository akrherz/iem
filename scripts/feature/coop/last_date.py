import psycopg2
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
import datetime
nt = NetworkTable("IACLIMATE")

pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""
 WITH lastdays as (
 SELECT station, year, min(extract(doy from day)) from alldata_ia where
 month > 7 and low <= 28 and year > 1950 and year < 2015
 GROUP by station, year)

 SELECT station, avg(min), count(*) from lastdays GROUP by station
""")

lats = []
lons = []
vals = []
dates = []
sites = []
for row in cursor:
    station = row[0]
    if station == 'IA0000' or station[2] == 'C':
        continue
    if station not in nt.sts:
        continue
    if station in ['IA3909', 'IA0364', 'IA3473', 'IA1394']:
        continue
    sites.append(station)
    lats.append(nt.sts[station]['lat'])
    lons.append(nt.sts[station]['lon'])
    vals.append(float(row[1]))
    d = datetime.date(2015, 1, 1) + datetime.timedelta(days=int(row[1]))
    dates.append(d.strftime("%-d %b"))

rng = range(int(min(vals)-2), int(max(vals)+4), 4)
labels = []
for i in rng:
    dt = datetime.date(2015, 1, 1) + datetime.timedelta(days=i)
    labels.append(dt.strftime("%-d %b"))

m = MapPlot(title=("Average First Date of Low Temperature "
                   "At or Below 28$^\circ$F"),
            subtitle="based on stations with data between 1951-2014")
m.contourf(lons, lats, vals, rng, clevlabels=labels,
           cmap=plt.get_cmap("jet"))
m.drawcounties()
# m.plot_values(lons, lats, dates, fmt='%s', labels=sites)
m.postprocess(filename='test.png')
