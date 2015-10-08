import psycopg2
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
nt = NetworkTable(("IACLIMATE"))
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
    WITH data as (
    SELECT station, year, sum(precip) as count from alldata_ia where
    year < 2015 and year > 1892 and precip >= 0.01 GROUP by station, year)

    SELECT station, count(*), avg(count) from data where station != 'IA0000'
    and substr(station,3,1) != 'C' GROUP by station
""")
vals = []
lats = []
lons = []
for row in cursor:
    if row[1] != 122:
        continue
    vals.append(float(row[2]))
    lons.append(nt.sts[row[0]]['lon'])
    lats.append(nt.sts[row[0]]['lat'])

m = MapPlot(sector='iowa', axisbg='white',
            title='1893-2014 Average Yearly Precipitation',
            subtitle='based on IEM Tracked Long Term Climate Sites')
m.plot_values(lons, lats, vals, '%.2f')
m.drawcounties()

m.postprocess(filename='test.png')
