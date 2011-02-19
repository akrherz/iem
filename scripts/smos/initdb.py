# Initially import the smos points into the database

import iemdb
SMOS = iemdb.connect('smos')
scursor = SMOS.cursor()

for line in open('/tmp/smos_grid.txt').readlines()[1:]:
    (id,lon,lat) = line.split(",")
    scursor.execute("""
    INSERT into grid(idx,geom) VALUES (%s, 'SRID=4326;POINT(%s %s)')
    """ % (id, lon, lat))

SMOS.commit()
    