#!/usr/bin/env python
''' Generate a WXC formatted file of DOT Snowplow positions '''
import sys
import memcache


def get_data():
    ''' Get the data we want and desire '''
    import datetime
    data = """Weather Central 001d0300 IDOT Snow Plows TimeStamp=%s
   6
   20 Station
   6 AIR TEMP F
   7 Lat
   9 Lon
   3 Heading
   3 SpeedMPH
""" % (datetime.datetime.utcnow().strftime("%Y.%m.%d.%H%M"),)

    import psycopg2
    postgis = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = postgis.cursor()

    cursor.execute("""
    SELECT ST_x(geom), ST_y(geom), label, airtemp, heading, velocity
    from idot_snowplow_current
    WHERE valid > now() - '30 minutes'::interval and velocity > 5
    and airtemp > -50 and airtemp < 100
    """)
    for row in cursor:
        data += ("%-20.20s %6.1f %7.4f %9.4f %3.0f %3.0f\n"
                 ) % (row[2], row[3], row[1], row[0], row[4], row[5])

    postgis.close()

    return data

if __name__ == '__main__':
    ''' Go main Go '''
    sys.stdout.write("Content-type: text/plain\n\n")

    mckey = '/request/wxc/idot_trucks.txt'
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = get_data()
        mc.set(mckey, res, 300)

    sys.stdout.write(res)
