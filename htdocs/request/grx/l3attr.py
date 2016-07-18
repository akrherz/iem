#!/usr/bin/env python
"""Placefile for NEXRAD l3 storm attributes
"""
import cgi
import sys
import memcache

ICONFILE = "http://mesonet.agron.iastate.edu/request/grx/storm_attribute.png"


def produce_content(nexrad):
    """Do Stuff"""
    import psycopg2.extras
    pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    limiter = ''
    threshold = 999
    title = "IEM NEXRAD L3 Attributes"
    if nexrad != '':
        limiter = " and nexrad = '%s' " % (nexrad,)
        title = "IEM %s NEXRAD L3 Attributes" % (nexrad,)
        threshold = 45
    cursor.execute("""
        SELECT *, ST_x(geom) as lon, ST_y(geom) as lat,
        valid at time zone 'UTC' as utc_valid
        from nexrad_attributes WHERE valid > now() - '15 minutes'::interval
    """ + limiter)
    res = ("Refresh: 3\n"
           "Threshold: %s\n"
           "Title: %s\n"
           "IconFile: 1, 32, 32, 16, 16, \"%s\"\n"
           "Font: 1, 11, 1, \"Courier New\"\n"
           ) % (threshold, title, ICONFILE)
    for row in cursor:
        text = ("K%s [%s] %s Z\\n"
                "Drct: %s Speed: %s kts\\n"
                ) % (row['nexrad'], row['storm_id'],
                     row['utc_valid'].strftime("%H:%i"), row['drct'],
                     row['sknt'])
        icon = 9
        if (row["tvs"] != "NONE" or row["meso"] != "NONE"):
            text += "TVS: %s MESO: %s\\n" % (row['tvs'], row['meso'])
        if (row['poh'] > 0 or row['posh'] > 0):
            text += "POH: %s POSH: %s MaxSize: %s\\n" % (row['poh'],
                                                         row['posh'],
                                                         row['max_size'])
            icon = 2
        if row['meso'] != 'NONE':
            icon = 6
        if row['tvs'] != 'NONE':
            icon = 5
        res += ("Object: %.4f,%.4f\n"
                "Threshold: 999\n"
                "Icon: 0,0,0,1,%s,\"%s\"\n"
                "END:\n"
                ) % (row['lat'], row['lon'], icon, text)
    return res


def main():
    """ Go Main Go """
    form = cgi.FieldStorage()
    nexrad = form.getfirst('nexrad', '').upper()[:3]

    mckey = "/request/grx/i3attr|%s" % (nexrad,)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = produce_content(nexrad)
        mc.set(mckey, res, 60)
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(res)

if __name__ == '__main__':
    main()
