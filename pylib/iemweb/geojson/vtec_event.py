""".. title:: VTEC Event GeoJSON Service

Return to `JSON Services </json/>`_

"""

import datetime

import simplejson as json
from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    wfo: str = Field("MPX", description="3 or 4 character WFO Identifier")
    year: int = Field(2015, description="Year of interest")
    phenomena: str = Field("SV", description="VTEC Phenomena", max_length=2)
    significance: str = Field(
        "W", description="VTEC Significance", max_length=1
    )
    etn: int = Field(1, description="VTEC Event ID")
    sbw: bool = Field(False, description="Include SBW polygons")
    lsrs: bool = Field(False, description="Include LSRs in the VTEC Event")


def run_lsrs(wfo, year, phenomena, significance, etn, sbw):
    """Do great things"""
    pgconn, cursor = get_dbconnc("postgis")

    if sbw == 1:
        sql = f"""
            SELECT distinct l.*, valid at time zone 'UTC' as utc_valid,
            ST_asGeoJson(l.geom) as geojson
            from lsrs l, sbw_{year} w WHERE
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
                from warnings_{year} w JOIN ugcs u on (u.gid = w.gid)
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
        "generation_time": datetime.datetime.utcnow().strftime(ISO8601),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                properties=dict(
                    utc_valid=row["utc_valid"].strftime(ISO8601),
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
    pgconn.close()
    return json.dumps(res)


def run_sbw(wfo, year, phenomena, significance, etn):
    """Do great things"""
    pgconn, cursor = get_dbconnc("postgis")

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
        "generation_time": datetime.datetime.utcnow().strftime(ISO8601),
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
    pgconn.close()
    return json.dumps(res)


def run(wfo, year, phenomena, significance, etn):
    """Do great things"""
    pgconn, cursor = get_dbconnc("postgis")

    cursor.execute(
        f"""
    SELECT
    w.ugc,
    ST_asGeoJson(u.geom) as geojson,
    issue at time zone 'UTC' as utc_issue,
    init_expire at time zone 'UTC' as utc_init_expire
    from warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
    WHERE w.wfo = %s and eventid = %s and
    phenomena = %s and significance = %s
    """,
        (wfo, etn, phenomena, significance),
    )
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.datetime.utcnow().strftime(ISO8601),
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
    pgconn.close()
    return json.dumps(res)


def get_mckey(environ):
    """Return the key."""
    return (
        f"/geojson/vtec_event/{environ['wfo']}/{environ['year']}/"
        f"{environ['phenomena']}/{environ['significance']}/"
        f"{environ['etn']}/{environ['sbw']}/{environ['lsrs']}"
    )


@iemapp(
    schema=Schema,
    help=__doc__,
    content_type="application/vnd.geo+json",
    memcacheexpire=3600,
    memcachekey=get_mckey,
)
def application(environ, start_response):
    """Main()"""
    headers = [("Content-type", "application/vnd.geo+json")]

    wfo = environ["wfo"]
    if len(wfo) == 4:
        wfo = wfo[1:]

    if environ["lsrs"]:
        res = run_lsrs(
            wfo,
            environ["year"],
            environ["phenomena"],
            environ["significance"],
            environ["etn"],
            environ["sbw"],
        )
    else:
        if environ["sbw"]:
            res = run_sbw(
                wfo,
                environ["year"],
                environ["phenomena"],
                environ["significance"],
                environ["etn"],
            )
        else:
            res = run(
                wfo,
                environ["year"],
                environ["phenomena"],
                environ["significance"],
                environ["etn"],
            )

    start_response("200 OK", headers)
    return res.encode("ascii")
