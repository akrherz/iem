""".. title:: GeoJSON of NWS COOP Reports for a given date

Return to `API Services </api/#json>`_

Documentation for /geojson/coopobs.py
=====================================

This service emits a given date's COOP observations.

Changelog
---------

- 2026-01-07: Initial Implementation

Example Requests
----------------

Return COOP reports valid 22 Oct 2024

https://mesonet.agron.iastate.edu/geojson/coopobs.py?valid=2024-10-22

"""

import json
from datetime import date, timezone

from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None,
        description="Optional JSONP callback function name",
    )
    valid: date = Field(
        default=date.today(),
        description="Date to generate data for",
        ge=date(2000, 1, 1),
        le=date(date.today().year, 12, 31),
    )


def p(val, precision=2):
    """see if we can round values better?"""
    if val is None:
        return None
    if 0 < val < 0.001:
        return "T"
    return round(val, precision)


@with_sqlalchemy_conn("iem")
def run(dt: date, conn: Connection | None = None):
    """Actually do the hard work of getting the current SPS in geojson"""

    res = conn.execute(
        sql_helper(
            """
        select id, ST_x(geom), ST_y(geom), coop_valid, pday, snow, snowd,
        extract(hour from coop_valid at time zone t.tzname)::int as hour,
        max_tmpf as high,
        min_tmpf as low, coop_tmpf, name, network, coop_valid, report
        from {table} s JOIN stations t ON (t.iemid = s.iemid)
        WHERE s.day = :dt and t.network ~* 'COOP' and coop_valid is not null
    """,
            table=f"summary_{dt:%Y}",
        ),
        {"dt": dt},
    )

    data = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utc().strftime(ISO8601),
        "count": res.rowcount,
    }
    for row in res.mappings():
        data["features"].append(
            dict(
                type="Feature",
                id=row["id"],
                properties=dict(
                    station=row["id"],
                    utc_valid=row["coop_valid"]
                    .astimezone(timezone.utc)
                    .strftime(ISO8601),
                    precip=p(row["pday"]),
                    snow=p(row["snow"], 1),
                    snowd=p(row["snowd"], 1),
                    name=row["name"],
                    hour=row["hour"],
                    high=row["high"],
                    low=row["low"],
                    coop_tmpf=row["coop_tmpf"],
                    network=row["network"],
                    report=row["report"],
                ),
                geometry=dict(
                    type="Point", coordinates=[row["st_x"], row["st_y"]]
                ),
            )
        )
    return json.dumps(data)


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=lambda x: f"/geojson/coopobs/{x['valid']}",
    memcacheexpire=300,
    content_type="application/vnd.geo+json",
)
def application(environ, start_response):
    """Do Workflow"""
    dt: date = environ["valid"]

    res = run(dt)
    headers = [("Content-type", "application/vnd.geo+json")]
    start_response("200 OK", headers)
    return res
