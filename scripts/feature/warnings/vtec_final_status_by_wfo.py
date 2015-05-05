import psycopg2
from pyiem.plot import MapPlot

dbconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = dbconn.cursor()

cursor.execute("""
 WITh data as (
 select wfo, phenomena, significance,
 extract(year from issue) as yr, count(*)
 from sbw WHERE issue > '2007-10-01' and
 issue < '2015-05-01' and phenomena = 'SV' and significance = 'W'
 GROUP by wfo, phenomena, significance, yr, eventid)

 SELECT wfo, sum(case when count > 2 then 1 else 0 end), count(*) from
 data GROUP by wfo
""")

data = {}
for row in cursor:
    data[row[0]] = row[1] / float(row[2]) * 100.

m = MapPlot(sector='nws', axisbg='white',
            title="Percentage of Severe T'Storm Warnings with 2 or more SVS Updates",
            subtitle='period: 1 Oct 2007 - 1 May 2015')

m.fill_cwas(data)

m.postprocess(filename='test.png')
