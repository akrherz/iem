
import psycopg2.extras
import calendar
from pyiem.plot import MapPlot
import matplotlib.cm as cm
import datetime

pgconn = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cursor.execute("""
        SELECT station, 
        sum(case when high > 32 and low < 32 then 1 else 0 end) as above,
        count(*) from alldata
        WHERE substr(station,3,1) = 'C' and month in (12,1,2) 
        GROUP by station""")
data = {}
for row in cursor:
    data[row['station']] = row['above'] / float(row['count']) * 100.

m = MapPlot(sector='midwest', axisbg='white',
                title='Percentage of Dec,Jan,Feb Days with High >32$^\circ$F + Low <32$^\circ$F',
                subtitle='By Climate District and Based on IEM Estimates')
cmap = cm.get_cmap("BrBG_r")
cmap.set_under('black')
cmap.set_over('black')
m.fill_climdiv(data, cmap=cmap)
m.postprocess(filename='test.png')
