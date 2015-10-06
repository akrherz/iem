import psycopg2.extras
from pyiem.plot import MapPlot
import matplotlib.cm as cm

pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cursor.execute("""
  with monthly as (
   SELECT station, extract(year from day + '40 days'::interval) as yr,
   avg((high+low)/2.) from alldata
   where month in (12,1,2) and substr(station,3,1) = 'C' GROUP by station, yr
   ),
   nextup as (
  SELECT station, yr, rank() OVER (PARTITION by station ORDER by avg ASC)
  from monthly
  )

  SELECT station, rank from nextup where yr = 2015
  """)
data = {}
for row in cursor:
    data[row['station']] = row['rank']

m = MapPlot(sector='midwest', axisbg='white',
            title='Dec 2014 - Jan/Feb 2015 Average Temperature Rank (1 is coldest)',
            subtitle='Based on IEM Estimates of Climate District Data (1893-2015)')
cmap = cm.get_cmap("BrBG_r")
cmap.set_under('black')
cmap.set_over('black')
m.fill_climdiv(data, cmap=cmap, bins=[1, 10, 25, 50, 75, 100, 115, 123])
m.postprocess(filename='test.png')
