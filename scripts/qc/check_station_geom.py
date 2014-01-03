"""
  Check to make sure the station metadata is reasonable!

"""
import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()

mcursor.execute("""
 SELECT id, network, ST_x(geom), ST_y(geom), modified from stations WHERE
 ST_x(geom) >= 180 or ST_x(geom) <= -180 or ST_y(geom) > 90 or ST_y(geom) < -90
""")
for row in mcursor:
    print 'check_station_geom.py LOC QC FAIL', row
