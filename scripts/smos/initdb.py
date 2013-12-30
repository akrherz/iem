# Initially import the smos points into the database

import psycopg2
SMOS = psycopg2.connect(database='smos', host='iemdb')
scursor = SMOS.cursor()

for line in open('/tmp/smos_grid.txt').readlines()[1:]:
    (sid,lon,lat) = line.split(",")
    scursor.execute("""
    INSERT into grid(idx,geom) VALUES (%s, 'SRID=4326;POINT(%s %s)')
    """ % (sid, lon, lat))

SMOS.commit()
    