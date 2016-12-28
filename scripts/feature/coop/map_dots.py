from pyiem.plot import MapPlot
import psycopg2
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')

df = read_sql("""SELECT ST_x(geom) as x, ST_y(geom) as y,
 min(min_tmpf) as val, state, count(*) from
 summary_2016 s JOIN stations t on (t.iemid = s.iemid) WHERE
 s.day > '2016-09-01' and min_tmpf is not null and t.country = 'US' and
 t.network ~* 'COOP' and t.state in ('IA', 'MN', 'ND', 'SD', 'NE',
 'KS', 'MO', 'WI', 'IL', 'IN', 'OH', 'MI', 'KY') GROUP by y, x, state
 ORDER by val ASC""", pgconn, index_col=None)
df = df[(df['count'] > 110)]

x3 = df[(df.val < 32) & (df.val >= 10)]
x2 = df[(df.val < 10) & (df.val > -10)]
x1 = df[(df.val < -10) & (df.val > -30)]
x0 = df[df.val < -30]

m = MapPlot(title='Fall 2016 Minimum Temperature Reports', axisbg='white',
            subtitle=('Based on NWS Cooperative Observer Data, '
                      'thru 27 Dec 2016'),
            sector='midwest')

x, y = m.map(tuple(x3.x), tuple(x3.y))
m.map.scatter(x, y, marker='o', color='g', s=50, zorder=1,
              label="10 to 32$^\circ$F")
x, y = m.map(tuple(x2.x), tuple(x2.y))
m.map.scatter(x, y, marker='s', color='b', zorder=1, s=50,
              label="-10 to 10$^\circ$F")
x, y = m.map(tuple(x1.x), tuple(x1.y))
m.map.scatter(x, y, marker='+', color='r', s=50, zorder=2,
              label="-30 to -10$^\circ$F")
x, y = m.map(tuple(x0.x), tuple(x0.y))
m.map.scatter(x, y, marker='v', facecolor='w', edgecolor='k', s=50, zorder=2,
              label="Sub -30$^\circ$F")

m.ax.legend(loc=4, scatterpoints=1, ncol=4)

m.postprocess(filename='test.png')
