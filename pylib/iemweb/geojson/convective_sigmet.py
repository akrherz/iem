""".. title:: Convective SIGMET GeoJSON

Return to `API Services </api/#json>`_

This service provides a GeoJSON representation of current Convective SIGMETs.

Changelog
---------

- 2025-05-13: Added `sts` and `ets` parameters to filter SIGMETs by time,
  must be less than 32 days in duration. Specifies the period of issuance.
- 2025-05-13: Added `at` parameter to provide SIGMETs at a specific time.
- 2024-08-14: Documentation Update

Example Requests
----------------

Get the current Convective SIGMETs

https://mesonet.agron.iastate.edu/geojson/convective_sigmet.geojson

Get the SIGMETs valid at 6 UTC on 10 Aug 2024

https://mesonet.agron.iastate.edu/geojson/convective_sigmet.geojson?\
at=2024-08-10T06:00:00Z

Get the SIGMETs valid between 6 UTC and 12 UTC on 10 Aug 2024

https://mesonet.agron.iastate.edu/geojson/convective_sigmet.geojson?\
sts=2024-08-10T06:00:00Z&ets=2024-08-10T12:00:00Z

"""

import json
from datetime import timedelta

from pydantic import AwareDatetime, Field, model_validator
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    at: AwareDatetime = Field(
        None,
        description="SIGMETs valid at given time, in ISO8601 format",
    )
    ets: AwareDatetime = Field(
        None,
        description="SIGMETs valid before time, in ISO8601 format",
    )
    sts: AwareDatetime = Field(
        None,
        description="SIGMETs valid after time, in ISO8601 format",
    )

    @model_validator(mode="after")
    def validate_time(self):
        """Ensure we have things that make sense."""
        # Ensure that sts and ets are both set or neither
        if self.sts and not self.ets:
            raise ValueError("If you set sts, you must also set ets")
        if self.ets and not self.sts:
            raise ValueError("If you set ets, you must also set sts")
        if (
            self.sts
            and self.ets
            and ((self.ets - self.sts) > timedelta(days=32))
        ):
            raise ValueError("Time filter needs to be less than 32 days")
        return self


@with_sqlalchemy_conn("postgis")
def run(environ: dict, conn: Connection = None) -> str:
    """Actually do the hard work of getting the current SBW in geojson"""
    timefilter = "issue <= :valid and expire > :valid"
    if environ["sts"]:
        timefilter = "issue >= :sts and issue < :ets"
    environ["valid"] = environ["at"] or utc()

    res = conn.execute(
        sql_helper(
            """
        SELECT *, ST_asGeoJson(geom) as geojson,
        issue at time zone 'UTC' as utc_issue,
        expire at time zone 'UTC' as utc_expire,
        label, product_id
        FROM sigmets_archive WHERE {timefilter} and sigmet_type = 'C'
        """,
            timefilter=timefilter,
        ),
        environ,
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
                properties={
                    "issue": row["utc_issue"].strftime(ISO8601),
                    "expire": row["utc_expire"].strftime(ISO8601),
                    "label": row["label"],
                    "product_id": row["product_id"],
                },
                geometry=json.loads(row["geojson"]),
            )
        )
    return json.dumps(data)


@iemapp(
    content_type="application/vnd.geo+json",
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Do Something"""
    # Go Main Go
    headers = [("Content-type", "application/vnd.geo+json")]

    res = run(environ)
    start_response("200 OK", headers)
    return res.encode("ascii")
