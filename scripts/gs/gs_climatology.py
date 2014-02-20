"""
 Generate
"""

from pyiem.plot import MapPlot
import datetime
import numpy as np
import psycopg2
COOP = psycopg2.connect("dbname=coop host=iemdb user=nobody")
ccursor = COOP.cursor()

ccursor.execute("""
WITH obs as (
    SELECT station, avg((high+low)/2.), sum(gdd50) from climate51 WHERE 
    extract(month from valid) in (5,6,7,8,9) GROUP by station)

SELECT ST_x(geom), ST_y(geom), avg, sum from obs o JOIN stations s ON
(s.id = o.station) WHERE s.network ~* 'CLIMATE' 
""")
lats = []
lons = []
vals = []
for row in ccursor:
    lats.append( row[1] )
    lons.append( row[0] )
    vals.append( row[3] )

m = MapPlot(sector='midwest', 
            title='1 May - 30 Sep Average Growing Degree Days Accumulation')
m.contourf(lons, lats, vals, np.arange(1600,3700,150), units='Fahrenheit')
m.postprocess(filename='test.png')
