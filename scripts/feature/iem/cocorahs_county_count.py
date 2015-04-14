import psycopg2
from pyiem.plot import MapPlot

iemdb = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = iemdb.cursor()

POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

icursor.execute("""
 WITH data as (
   SELECT distinct s.iemid from summary s JOIN stations t on (t.iemid = s.iemid)
   WHERE t.network = 'IACOCORAHS' and s.day > '2014-04-12' and pday > 0)

 SELECT ugc_county, count(*) from stations t JOIN data d on (d.iemid = t.iemid)
 GROUP by ugc_county ORDER by count DESC
""")

data = {}
for row in icursor:
    data[row[0]] = row[1]

# Query out centroids of counties...
pcursor.execute("""SELECT ugc, ST_x(ST_centroid(geom)) as lon, 
  ST_y(ST_centroid(geom)) as lat 
 from ugcs WHERE state = 'IA' and end_ts is null and substr(ugc,3,1) = 'C'""")
clons = []
clats = []
cvals = []
for row in pcursor:
    cvals.append(data.get(row[0],0))
    clats.append(row[2])
    clons.append(row[1])


m = MapPlot(axisbg='white', title='Iowa CoCoRaHS Observers Per County',
            subtitle='Sites with at least one report in past year (Apr 2014-2015)')
m.fill_ugc_counties(data, [1,2,3,4,5,7,10,15,20])
m.plot_values(clons, clats, cvals)
m.drawcounties()
m.postprocess(filename='test.png')