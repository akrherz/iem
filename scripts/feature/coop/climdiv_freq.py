
import psycopg2.extras
import calendar
from pyiem.plot import MapPlot
import matplotlib.cm as cm
import datetime

pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cursor.execute("""
  with monthly as (
   SELECT station, year, avg((high+low)/2.) from alldata
   where month = 2 and substr(station,3,1) = 'C' GROUP by station, year
   ),
   nextup as (
  SELECT station, year, rank() OVER (PARTITION by station ORDER by avg ASC)
  from monthly
  )

  SELECT station, rank from nextup where year = 2015
  """)
data = {}
for row in cursor:
    data[row['station']] = row['rank']

m = MapPlot(sector='midwest', axisbg='white',
            title='February Average Temperature Rank (1 is coldest)',
            subtitle='Based on IEM Estimates of Climate District Data (1893-2015)')
cmap = cm.get_cmap("BrBG_r")
cmap.set_under('black')
cmap.set_over('black')
m.fill_climdiv(data, cmap=cmap)
m.postprocess(filename='test.png')
