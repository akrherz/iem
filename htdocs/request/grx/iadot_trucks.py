#!/usr/bin/env python
"""
 Placefile for DOT trucks and webcam images
"""
import sys
import memcache
import datetime

URLBASE = "https://mesonet.agron.iastate.edu/data/camera/idot_trucks"


def s2icon(s):
    """ Convert heading """
    if s < 2.5:
        return "1,21"
    if s < 5:
        return "1,1"
    if s < 10:
        return "1,2"
    if s < 15:
        return "1,3"
    if s < 20:
        return "1,4"
    if s < 25:
        return "1,5"
    if s < 30:
        return "1,6"
    if s < 35:
        return "1,7"

    if s < 40:
        return "1,8"
    if s < 45:
        return "1,9"
    if s < 50:
        return "1,10"
    if s < 55:
        return "1,11"
    if s < 60:
        return "1,12"
    if s < 65:
        return "1,13"
    if s < 70:
        return "1,14"

    if s < 75:
        return "1,15"
    if s < 80:
        return "1,16"
    if s < 85:
        return "1,17"
    if s < 80:
        return "1,18"
    if s < 100:
        return "1,19"
    return "1,20"


def produce_content():
    """ Generate content """
    import psycopg2

    res = """Title: Iowa DOT Trucks @%sZ
Refresh: 5
Color: 200 200 255
IconFile: 1, 18, 32, 2, 31, "http://www.tornadocentral.com/grlevel3/windbarbs.png"
IconFile: 2, 15, 15, 8, 8, "http://www.tornadocentral.com/grlevel3/cloudcover.png"
IconFile: 3, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"
Font: 1, 11, 1, "Courier New"

""" % (datetime.datetime.utcnow().strftime("%H%M"), )

    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor()

    # cursor.execute("""SELECT label, valid, ST_x(geom), ST_y(geom) from
    # idot_dashcam_current where valid > (now() - '1 hour'::interval)""")
    # res1 = ""
    # res2 = ""
    # for i, row in enumerate(cursor):
    #    url = "%s/%s.jpg" % (URLBASE, row[0])
    #    res1 += "IconFile: %s, 320, 240, 0, 0,\"%s\"\n" % (i+4, url)
    #    res2 += "Icon: %.4f,%.4f,000,%s,1\n" % (row[3], row[2], i+4)
    #
    # res += res1
    # res += res2

    cursor.execute("""SELECT valid, heading, velocity, roadtemp, airtemp,
    solidmaterial, liquidmaterial, prewetmaterial, solidsetrate,
    liquidsetrate, prewetsetrate, solid_spread_code, road_temp_code,
    ST_x(geom), ST_y(geom), label from idot_snowplow_current
    where valid > (now() - '1 hour'::interval) and
    valid < (now() + '1 hour'::interval) ORDER by label ASC""")

    for row in cursor:
        txt = ("%s @ %s\\nRoad Temp: %s\\nVelocity: %s MPH\\nAir Temp: %s\\n"
               ) % (row[15],
                    row[0].strftime("%d %b %I:%M %p"), row[3], row[2], row[4])
        res += "Object: %.6f, %.6f\n" % (row[14], row[13])
        res += "Threshold: 999\n"
        res += "Icon: 0,0,%s,3,7\n" % (0 if row[1] is None else int(row[1]),)
        res += "Icon: 0,0,000,2,13,\"%s\"\n" % (txt, )
        res += "End:\n\n"

    return res


def main():
    """ Go Main Go """
    sys.stdout.write("Content-type: text/plain\n\n")

    mckey = "/request/grx/iadot_trucks.txt"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = produce_content()
        mc.set(mckey, res, 300)
    sys.stdout.write(res)

if __name__ == '__main__':
    main()
