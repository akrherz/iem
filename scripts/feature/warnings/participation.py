import matplotlib.colors as mpcolors
import matplotlib.cm as cm
import psycopg2
import numpy as np

from pyiem.plot import MapPlot
POSTGIS = psycopg2.connect(database='postgis', host='localhost', user='nobody',
                           port=5555)
pcursor = POSTGIS.cursor()

cmap = cm.get_cmap("Accent")
cmap.set_under("#ffffff")
cmap.set_over("black")

m = MapPlot(sector='nws', axisbg='#EEEEEE',
            title='1+ TOR warn for 100 most active TOR warn days 1986-2015',
            subtitle='A day is defined as 12 to12 UTC period, did the county get 1+ warning during those 100 events?',
            cwas=True)

bins = np.arange(0, 101, 10)
bins[0] = 1
norm = mpcolors.BoundaryNorm(bins, cmap.N)


pcursor.execute("""
 WITH data as (
  SELECT ugc, date(issue at time zone 'UTC' + '12 hours'::interval)
  from warnings where phenomena in ('TO') and significance = 'W'
  ),
 maxdays as (
  SELECT date, count(*) from data GROUP by date ORDER by count DESC LIMIT 100
 ),
 events as (
 SELECT distinct ugc, d.date from data d JOIN maxdays m on (m.date = d.date)
 )

 SELECT ugc, count(*) from events GROUP by ugc
""")
data = {}
for row in pcursor:
    data[row[0]] = float(row[1])

m.fill_ugc_counties(data, bins, cmap=cmap, units='Count')
m.postprocess(filename='test.png')
