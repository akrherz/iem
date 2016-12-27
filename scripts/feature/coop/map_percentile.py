import psycopg2
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
nt = NetworkTable("IACLIMATE")
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 WITH yearly as (
   SELECT station, year, sum(precip) from alldata_ia where
   station in (select distinct station from alldata_ia where year = 1893)
   and year > 1892 GROUP by station, year)

 SELECT station, sum(case when sum > 41.14 then 1 else 0 end), count(*)
 from yearly GROUP by station ORDER by sum ASC

""")
lats = []
lons = []
ranks = []
for row in cursor:
    if row[0][2] == 'C' or row[0] in ['IA0000']:
        continue
    print row

    lats.append(nt.sts[row[0]]['lat'])
    lons.append(nt.sts[row[0]]['lon'])
    ranks.append(row[1])

m = MapPlot(title="Where would Sioux City's 41.14 inch 2014 Total Rank?",
            subtitle=('period 1893-2014, number of years (out of 122) '
                      'with local total over 41.14 inches'),
            drawstates=True, axisbg='white')
m.plot_values(lons, lats, ranks, textsize=20, color='r')
m.drawcounties()

m.makefeature()
