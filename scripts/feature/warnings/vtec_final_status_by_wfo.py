import psycopg2
from pyiem.plot import MapPlot

dbconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = dbconn.cursor()

cursor.execute("""
 select wfo, sum(case when polygon_end = init_expire then 1 else 0 end),
 count(*) from sbw WHERE status = 'NEW' and issue > '2007-10-01' and
 issue < '2015-05-01' and phenomena = 'TO' and significance = 'W'
 GROUP by wfo
""")

data = {}
for row in cursor:
    data[row[0]] = row[1] / float(row[2]) * 100.

m = MapPlot(sector='nws', axisbg='white',
            title="Percentage of Tornado Warnings without SVS Update",
            subtitle='period: 1 Oct 2007 - 1 May 2015')

m.fill_cwas(data)

m.postprocess(filename='test.png')
