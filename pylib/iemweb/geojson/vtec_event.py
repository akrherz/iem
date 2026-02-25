""".. title:: VTEC Event GeoJSON Service

Return to `API Services </api/#json>`_. This service drives some of the data
shown on the `VTEC Browser </vtec/>`_.

Documentation for /geojson/vtec_event.py
----------------------------------------

This service emits a GeoJSON for a single VTEC event.  The payload can include
some additional requested metadata.

Changelog
---------

- 2026-02-24: For IEM consistency, the root metadata `generation_time` was
  renamed `generated_at`.
- 2024-08-16: Initial documentation update

Example Usage
-------------

Return information about Des Moines Tornado Warning 49 from 2024

https://mesonet.agron.iastate.edu/geojson/vtec_event.py\
?wfo=DMX&year=2024&phenomena=TO&significance=W&etn=49

Return Local Storm Reports associated with the above event

https://mesonet.agron.iastate.edu/geojson/vtec_event.py\
?wfo=DMX&year=2024&phenomena=TO&significance=W&etn=49&lsrs=1

Return Local Storm Reports associated with the above event, but confined to
the Storm Based Warning polygon

https://mesonet.agron.iastate.edu/geojson/vtec_event.py\
?wfo=DMX&year=2024&phenomena=TO&significance=W&etn=49&lsrs=1&sbw=1

Return Storm Based Warning polygons associated with the above event

https://mesonet.agron.iastate.edu/geojson/vtec_event.py\
?wfo=DMX&year=2024&phenomena=TO&significance=W&etn=49&sbw=1

"""

from datetime import datetime, timezone
from typing import Annotated

import simplejson as json
from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="JSONP callback function name")
    ] = None
    wfo: Annotated[
        str,
        Field(
            description="3 or 4 character WFO Identifier",
            min_length=3,
            max_length=4,
        ),
    ] = "MPX"
    year: Annotated[int, Field(description="Year of interest")] = 2015
    phenomena: Annotated[
        str, Field(description="VTEC Phenomena", max_length=2)
    ] = "SV"
    significance: Annotated[
        str, Field(description="VTEC Significance", max_length=1)
    ] = "W"
    etn: Annotated[int, Field(description="VTEC Event ID", ge=1, le=9999)] = 1
    sbw: Annotated[
        bool,
        Field(
            description=(
                "Confine result to include the Storm Based Warning polygon"
            ),
        ),
    ] = False
    lsrs: Annotated[
        bool,
        Field(
            description=(
                "Provide Local Storm Reports either for the county or "
                "SBW when sbw=1 is set"
            ),
        ),
    ] = False


def run_lsrs(wfo, year, phenomena, significance, etn, sbw):
    """Do great things"""
    pgconn, cursor = get_dbconnc("postgis")

    if sbw == 1:
        sql = """
            SELECT distinct l.*, valid at time zone 'UTC' as utc_valid,
            ST_asGeoJson(l.geom) as geojson,
            coalesce(l.product_id, l.product_id_summary) as product_id
            from lsrs l, sbw w WHERE w.vtec_year = %s and
            l.geom && w.geom and ST_contains(w.geom, l.geom)
            and l.wfo = %s and
            l.valid >= w.issue and l.valid <= w.expire and
            w.wfo = %s and w.eventid = %s and
            w.significance = %s and w.phenomena = %s
            ORDER by l.valid ASC
        """
        args = (year, wfo, wfo, etn, significance, phenomena)
    else:
        sql = """
            WITH countybased as (
                SELECT min(issue) as issued, max(expire) as expired
                from warnings w JOIN ugcs u on (u.gid = w.gid)
                WHERE w.vtec_year = %s and w.wfo = %s and w.eventid = %s and
                w.significance = %s
                and w.phenomena = %s)

            SELECT distinct l.*, valid at time zone 'UTC' as utc_valid,
            ST_asGeoJson(l.geom) as geojson,
            coalesce(l.product_id, l.product_id_summary) as product_id
            from lsrs l, countybased c WHERE
            l.valid >= c.issued and l.valid < c.expired and
            l.wfo = %s ORDER by l.valid ASC
        """
        args = (year, wfo, etn, significance, phenomena, wfo)
    cursor.execute(sql, args)
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.now(timezone.utc).strftime(ISO8601),
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
                    product_id=row["product_id"],
                ),
                geometry=json.loads(row["geojson"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


def run_sbw(wfo, year, phenomena, significance, etn):
    """Do great things"""
    pgconn, cursor = get_dbconnc("postgis")

    cursor.execute(
        """
    SELECT
    ST_asGeoJson(geom) as geojson,
    issue at time zone 'UTC' as utc_issue,
    init_expire at time zone 'UTC' as utc_init_expire
    from sbw WHERE vtec_year = %s and wfo = %s
    and eventid = %s and phenomena = %s and significance = %s
    and status = 'NEW'
    """,
        (year, wfo, etn, phenomena, significance),
    )
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": datetime.now(timezone.utc).strftime(ISO8601),
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
        """
    SELECT
    w.ugc,
    ST_asGeoJson(u.geom) as geojson,
    issue at time zone 'UTC' as utc_issue,
    init_expire at time zone 'UTC' as utc_init_expire
    from warnings w JOIN ugcs u on (w.gid = u.gid)
    WHERE w.vtec_year = %s and w.wfo = %s and eventid = %s and
    phenomena = %s and significance = %s
    """,
        (year, wfo, etn, phenomena, significance),
    )
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generated_at": utc().strftime(ISO8601),
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


def get_mckey(environ: dict) -> str:
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
