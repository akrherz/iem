from pyiem.plot import MapPlot
import psycopg2
import pandas as pd

pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT ST_x(geom), ST_y(geom), min(min_tmpf) from
 summary_2015 s JOIN stations t on (t.iemid = s.iemid) WHERE
 s.day > '2015-09-01' and min_tmpf > 0 and t.country = 'US' and
 t.network ~* 'COOP' and t.state in ('IA', 'MN', 'ND', 'SD', 'NE',
 'KS', 'MO', 'WI', 'IL', 'IN', 'OH', 'MI', 'KY') GROUP by st_y, st_x
 ORDER by min ASC""")
res = []
for row in cursor:
    res.append(dict(val=row[2], x=row[0], y=row[1]))

df = pd.DataFrame(res)

x35 = df[(df.val < 36) & (df.val >= 32)]
x32 = df[(df.val < 32) & (df.val > 28)]
x29 = df[df.val < 29]

m = MapPlot(title='Fall 2015 Minimum Temperature Reports', axisbg='white',
            subtitle='Based on NWS Cooperative Observer Data, thru 7 Oct 2015',
            sector='midwest')

x, y = m.map(tuple(x35.x), tuple(x35.y))
m.map.scatter(x, y, marker='o', color='g', s=50, zorder=1,
              label="Sub 36$^\circ$F")
x, y = m.map(tuple(x32.x), tuple(x32.y))
m.map.scatter(x, y, marker='s', zorder=1, s=50,
              label="Sub 32$^\circ$F")
x, y = m.map(tuple(x29.x), tuple(x29.y))
m.map.scatter(x, y, marker='+', color='r', s=50, zorder=2,
              label="Sub 29$^\circ$F")

m.ax.legend(loc=4, scatterpoints=1)

m.postprocess(filename='test.png')
