from pyiem.plot import MapPlot
import psycopg2
import pandas as pd

pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()

cursor.execute("""SELECT ST_x(geom), ST_y(geom), min(min_tmpf) from
 summary_2014 s JOIN stations t on (t.iemid = s.iemid) WHERE
 s.day > '2014-05-12' and min_tmpf > 0 and t.country = 'US' and
 t.network ~* 'COOP' GROUP by st_y, st_x
 ORDER by min ASC""")
res = []
for row in cursor:
    res.append( dict(val=row[2], x=row[0], y=row[1]) )

df = pd.DataFrame(res)

x32 = df[(df.val<32)&(df.val>28)]
x29 = df[df.val<29]

m = MapPlot(title='13-19 May 2014 Freezing Reports',
            subtitle='Based on NWS Cooperative Observer Data',
            sector='midwest')

x,y = m.map(x32.x, x32.y)
m.map.scatter(x,y, marker='s',zorder=1, label="Sub 32$^\circ$F")
x,y = m.map(x29.x, x29.y)
m.map.scatter(x,y, marker='+', color='r', s=40, zorder=2, label="Sub 29$^\circ$F")

m.ax.legend(loc=4, scatterpoints=1)

m.postprocess(filename='test.ps')
import iemplot
iemplot.makefeature('test')


