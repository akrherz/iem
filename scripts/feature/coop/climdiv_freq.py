
import psycopg2.extras
import calendar
from pyiem.plot import MapPlot
import matplotlib.cm as cm
import datetime

pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cursor.execute("""
  WITH yearmax as (
    SELECT station, max(high),
    extract(year from day + '35 days'::interval) as yr from alldata
    WHERE substr(station,3,1) = 'C' and month in (12,1,2) GROUP by station, yr
  )
  SELECT station, sum(case when max < 50 then 1 else 0 end), count(*)
  from yearmax GROUP by station""")
data = {}
for row in cursor:
    data[row['station']] = row['sum'] / float(row['count']) * 100.

m = MapPlot(sector='midwest', axisbg='white',
            title='Percentage of Winters Seasons Where High failed to Reach 50$^\circ$F',
            subtitle='Max Daily High Over Dec,Jan,Feb By Climate District; Based on IEM Estimates (1893-2014)')
cmap = cm.get_cmap("BrBG_r")
cmap.set_under('black')
cmap.set_over('black')
m.fill_climdiv(data, cmap=cmap)
m.postprocess(filename='test.png')
