import psycopg2
from pyiem.plot import MapPlot

dbconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = dbconn.cursor()

cursor.execute("""
 SELECT wfo, sum(case when status = 'NEW' then 1 else 0 end), count(*) from
 warnings where phenomena = 'SV' and significance = 'W' and gtype = 'P'
 and issue > '2007-10-01' GROUP by wfo
""")

data = {}
for row in cursor:
    data[ row[0] ] = row[1] / float(row[2]) * 100.

m = MapPlot(sector='nws',
            title="Percentage of Severe T'Storm Warnings without SVS Update",
            subtitle='period: 1 Oct 2007 - 21 Jun 2013')

m.fill_cwas(data)

m.postprocess(filename='test.png')