""" Generate a GeoJSON of 7 AM precip data """
import datetime
import json

import memcache
import psycopg2.extras
import pytz
from paste.request import parse_formvars
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconn, html_escape


def p(val, precision=2):
    """see if we can round values better?"""
    if val is None:
        return None
    if 0 < val < 0.001:
        return TRACE_VALUE
    return round(val, precision)


def router(group, ts):
    """Figure out which report to generate

    Args:
      group (str): the switch string indicating group
      ts (date): date we are interested in
    """
    if group == "coop":
        return run(ts)
    if group == "azos":
        return run_azos(ts)
    return None


def run_azos(ts):
    """ Get the data please """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utcnow = datetime.datetime.utcnow()
    # Now we have the tricky work of finding what 7 AM is
    ts = ts.astimezone(pytz.timezone("America/Chicago"))
    ts1 = ts.replace(hour=7)
    ts0 = ts1 - datetime.timedelta(hours=24)
    cursor.execute(
        "select t.id, t.name, sum(phour), st_x(geom), st_y(geom) "
        "from hourly h JOIN stations t ON "
        "(h.iemid = t.iemid) where t.network in ('AWOS', 'IA_ASOS') and "
        "valid >= %s and valid < %s GROUP by t.id, t.name, t.geom",
        (ts0, ts1),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    pday=p(row["sum"]), snow=None, snowd=None, name=row["name"]
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )

    return json.dumps(res)


def run(ts):
    """ Actually do the hard work of getting the current SPS in geojson """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    utcnow = datetime.datetime.utcnow()

    cursor.execute(
        """
        select id, ST_x(geom), ST_y(geom), coop_valid, pday, snow, snowd,
        name from summary s JOIN stations t ON (t.iemid = s.iemid)
        WHERE s.day = %s and t.network = 'IA_COOP' and pday >= 0
        and extract(hour from coop_valid) between 5 and 10
    """,
        (ts.date(),),
    )

    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    pday=p(row["pday"]),
                    snow=p(row["snow"], 1),
                    snowd=p(row["snowd"], 1),
                    name=row["name"],
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Do Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    form = parse_formvars(environ)
    group = form.get("group", "coop")
    cb = form.get("callback", None)
    dt = form.get("dt", datetime.date.today().strftime("%Y-%m-%d"))
    ts = datetime.datetime.strptime(dt, "%Y-%m-%d")
    ts = ts.replace(hour=12, tzinfo=pytz.utc)

    mckey = "/geojson/7am/%s/%s" % (dt, group)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = router(group, ts)
        mc.set(mckey, res, 15)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    start_response("200 OK", headers)
    return [data.encode("ascii")]


if __name__ == "__main__":
    run(datetime.datetime(2020, 9, 9))
