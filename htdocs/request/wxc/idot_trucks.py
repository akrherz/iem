"""Generate a WXC formatted file of DOT Snowplow positions"""
import datetime

from pyiem.util import get_dbconn
from pyiem.webutil import iemapp
from pymemcache.client import Client


def get_data():
    """Get the data we want and desire"""
    data = """Weather Central 001d0300 IDOT Snow Plows TimeStamp=%s
   6
   20 Station
   6 AIR TEMP F
   7 Lat
   9 Lon
   3 Heading
   3 SpeedMPH
""" % (
        datetime.datetime.utcnow().strftime("%Y.%m.%d.%H%M"),
    )

    postgis = get_dbconn("postgis")
    cursor = postgis.cursor()

    cursor.execute(
        """
    SELECT ST_x(geom), ST_y(geom), label, airtemp, heading, velocity
    from idot_snowplow_current
    WHERE valid > now() - '30 minutes'::interval and velocity > 5
    and airtemp > -50 and airtemp < 100
    """
    )
    for row in cursor:
        data += ("%-20.20s %6.1f %7.4f %9.4f %3.0f %3.0f\n") % (
            row[2],
            row[3],
            row[1],
            row[0],
            row[4],
            row[5],
        )

    postgis.close()

    return data


@iemapp()
def application(_environ, start_response):
    """Go Main Go"""
    start_response("200 OK", [("Content-type", "text/plain")])

    mckey = "/request/wxc/idot_trucks.txt"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = get_data()
        mc.set(mckey, res, 300)
    else:
        res = res.decode("utf-8")
    mc.close()
    return [res.encode("ascii")]
