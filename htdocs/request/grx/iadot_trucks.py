"""
 Placefile for DOT trucks and webcam images
"""
import datetime

from pymemcache.client import Client
from pyiem.util import get_dbconn

URLBASE = "https://mesonet.agron.iastate.edu/data/camera/idot_trucks"
ARROWS = "https://mesonet.agron.iastate.edu/request/grx/arrows.png"


def produce_content():
    """Generate content"""

    res = """Title: Iowa DOT Trucks @%sZ
Refresh: 5
Color: 200 200 255
IconFile: 1, 15, 25, 8, 25, "%s"
Font: 1, 11, 1, "Courier New"

""" % (
        datetime.datetime.utcnow().strftime("%H%M"),
        ARROWS,
    )

    pgconn = get_dbconn("postgis", user="nobody")
    cursor = pgconn.cursor()

    cursor.execute(
        """
        SELECT valid, heading, velocity, roadtemp, airtemp,
        solidmaterial, liquidmaterial, prewetmaterial, solidsetrate,
        liquidsetrate, prewetsetrate, solid_spread_code, road_temp_code,
        ST_x(geom), ST_y(geom), label from idot_snowplow_current
        where valid > (now() - '1 hour'::interval) and
        valid < (now() + '1 hour'::interval) ORDER by label ASC
    """
    )

    for row in cursor:
        txt = (
            "%s @ %s\\nRoad Temp: %s\\nVelocity: %s MPH\\nAir Temp: %s\\n"
        ) % (
            row[15],
            row[0].strftime("%d %b %I:%M %p"),
            row[3],
            row[2],
            row[4],
        )
        res += "Object: %.6f, %.6f\n" % (row[14], row[13])
        res += "Threshold: 999\n"
        res += ('Icon: 0,0,%s,1,7,"%s"\n') % (
            0 if row[1] is None else int(row[1]),
            txt,
        )
        res += "End:\n\n"

    return res


def application(_environ, start_response):
    """Go Main Go"""
    start_response("200 OK", [("Content-type", "text/plain")])

    mckey = "/request/grx/iadot_trucks.txt"
    mc = Client(["iem-memcached", 11211])
    res = mc.get(mckey)
    if not res:
        res = produce_content()
        mc.set(mckey, res, 300)
    else:
        res = res.decode("utf-8")
    mc.close()
    return [res.encode("ascii")]
