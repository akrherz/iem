""" Generate a GeoJSON of 7 AM precip data """
import datetime
import json
from zoneinfo import ZoneInfo

from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconnc, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


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
        return run(
            ts,
            [
                "IA_COOP",
                "MO_COOP",
                "KS_COOP",
                "NE_COOP",
                "SD_COOP",
                "MN_COOP",
                "WI_COOP",
                "IL_COOP",
            ],
        )
    if group == "azos":
        return run_azos(ts)
    if group == "cocorahs":
        return run(ts, ["IACOCORAHS"])
    return None


def run_azos(ts):
    """Get the data please"""
    pgconn, cursor = get_dbconnc("iem")

    utcnow = datetime.datetime.utcnow()
    # Now we have the tricky work of finding what 7 AM is
    ts = ts.astimezone(ZoneInfo("America/Chicago"))
    ts1 = ts.replace(hour=7)
    ts0 = ts1 - datetime.timedelta(hours=24)
    cursor.execute(
        """
        select t.id, t.name, t.network, sum(phour), st_x(geom), st_y(geom)
        from hourly h JOIN stations t ON
        (h.iemid = t.iemid) where t.network in ('IA_ASOS', 'SD_ASOS',
        'NE_ASOS', 'KS_ASOS', 'MO_ASOS', 'IL_ASOS', 'WI_ASOS', 'MN_ASOS')
        and valid >= %s and valid < %s GROUP by t.id, t.network, t.name, t.geom
        """,
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
                    pday=p(row["sum"]),
                    snow=None,
                    snowd=None,
                    name=row["name"],
                    network=row["network"],
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )
    pgconn.close()
    return json.dumps(res)


def run(ts, networks):
    """Actually do the hard work of getting the current SPS in geojson"""
    pgconn, cursor = get_dbconnc("iem")

    utcnow = datetime.datetime.utcnow()

    cursor.execute(
        """
        select id, ST_x(geom), ST_y(geom), coop_valid, pday, snow, snowd,
        extract(hour from coop_valid)::int as hour, max_tmpf as high,
        min_tmpf as low, coop_tmpf, name, network
        from summary s JOIN stations t ON (t.iemid = s.iemid)
        WHERE s.day = %s and t.network = ANY(%s) and pday >= 0
        and extract(hour from coop_valid) between 5 and 10
    """,
        (ts.date(), networks),
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
                    hour=row["hour"],
                    high=row["high"],
                    low=row["low"],
                    coop_tmpf=row["coop_tmpf"],
                    network=row["network"],
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )
    pgconn.close()
    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Do Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    group = environ.get("group", "coop")
    cb = environ.get("callback", None)
    dt = environ.get("dt", datetime.date.today().strftime("%Y-%m-%d"))
    try:
        ts = datetime.datetime.strptime(dt, "%Y-%m-%d")
    except ValueError:
        raise IncompleteWebRequest("dt variable should be in form YYYY-MM-DD")
    ts = ts.replace(hour=12, tzinfo=ZoneInfo("UTC"))

    mckey = f"/geojson/7am/{dt}/{group}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if res is None:
        res = router(group, ts)
        mc.set(mckey, res, 15)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]


if __name__ == "__main__":
    run(datetime.datetime(2020, 9, 9))
