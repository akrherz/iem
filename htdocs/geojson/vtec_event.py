"""GeoJSON source for VTEC event"""
import datetime
import json

import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape
from pymemcache.client import Client

ISO = "%Y-%m-%dT%H:%M:%SZ"


def run_lsrs(wfo, year, phenomena, significance, etn, sbw):
    """Do great things"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sbwtable = f"sbw_{year}"
    warningtable = f"warnings_{year}"
    if sbw == 1:
        sql = f"""
            SELECT distinct l.*, valid at time zone 'UTC' as utc_valid,
            ST_asGeoJson(l.geom) as geojson
            from lsrs l, {sbwtable} w WHERE
            l.geom && w.geom and ST_contains(w.geom, l.geom)
            and l.wfo = %s and
            l.valid >= w.issue and l.valid <= w.expire and
            w.wfo = %s and w.eventid = %s and
            w.significance = %s and w.phenomena = %s
            ORDER by l.valid ASC
        """
        args = (wfo, wfo, etn, significance, phenomena)
    else:
        sql = f"""
            WITH countybased as (
                SELECT min(issue) as issued, max(expire) as expired
                from {warningtable} w JOIN ugcs u on (u.gid = w.gid)
                WHERE w.wfo = %s and w.eventid = %s and
                w.significance = %s
                and w.phenomena = %s)

            SELECT distinct l.*, valid at time zone 'UTC' as utc_valid,
            ST_asGeoJson(l.geom) as geojson
            from lsrs l, countybased c WHERE
            l.valid >= c.issued and l.valid < c.expired and
            l.wfo = %s ORDER by l.valid ASC
        """
        args = (wfo, etn, significance, phenomena, wfo)
    cursor.execute(sql, args)
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                properties=dict(
                    utc_valid=row["utc_valid"].strftime(ISO),
                    event=row["typetext"],
                    type=row["type"],
                    magnitude=row["magnitude"],
                    city=row["city"],
                    county=row["county"],
                    remark=row["remark"],
                ),
                geometry=json.loads(row["geojson"]),
            )
        )

    return json.dumps(res)


def run_sbw(wfo, year, phenomena, significance, etn):
    """Do great things"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    table = f"sbw_{year}"
    cursor.execute(
        f"""
    SELECT
    ST_asGeoJson(geom) as geojson,
    issue at time zone 'UTC' as utc_issue,
    init_expire at time zone 'UTC' as utc_init_expire
    from {table}
    WHERE wfo = %s and eventid = %s and phenomena = %s and significance = %s
    and status = 'NEW'
    """,
        (wfo, etn, phenomena, significance),
    )
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                properties=dict(
                    phenomena=phenomena, significance=significance, eventid=etn
                ),
                geometry=json.loads(row["geojson"]),
            )
        )

    return json.dumps(res)


def run(wfo, year, phenomena, significance, etn):
    """Do great things"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    table = f"warnings_{year}"
    cursor.execute(
        f"""
    SELECT
    w.ugc,
    ST_asGeoJson(u.geom) as geojson,
    issue at time zone 'UTC' as utc_issue,
    init_expire at time zone 'UTC' as utc_init_expire
    from {table} w JOIN ugcs u on (w.gid = u.gid)
    WHERE w.wfo = %s and eventid = %s and
    phenomena = %s and significance = %s
    """,
        (wfo, etn, phenomena, significance),
    )
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["ugc"],
                properties=dict(
                    phenomena=phenomena, significance=significance, eventid=etn
                ),
                geometry=json.loads(row["geojson"]),
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Main()"""
    headers = [("Content-type", "application/vnd.geo+json")]

    form = parse_formvars(environ)
    wfo = form.get("wfo", "MPX")
    if len(wfo) == 4:
        wfo = wfo[1:]
    year = int(form.get("year", 2015))
    phenomena = form.get("phenomena", "SV")[:2]
    significance = form.get("significance", "W")[:1]
    etn = int(form.get("etn", 1))
    sbw = int(form.get("sbw", 0))
    lsrs = int(form.get("lsrs", 0))
    cb = form.get("callback", None)

    mckey = (
        f"/geojson/vtec_event/{wfo}/{year}/{phenomena}/{significance}/"
        f"{etn}/{sbw}/{lsrs}"
    )
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        if lsrs == 1:
            res = run_lsrs(wfo, year, phenomena, significance, etn, sbw)
        else:
            if sbw == 1:
                res = run_sbw(wfo, year, phenomena, significance, etn)
            else:
                res = run(wfo, year, phenomena, significance, etn)
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
