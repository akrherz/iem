""".. title:: DCP Variables Metadata Service

Return to `JSON Services </json/>`.

Documentation for /json/dcp_vars.json
-------------------------------------

The IEM attempts a robust processing of HADS/DCP data in SHEF format.  This
SHEF format carries a huge number of potential variable names.  This service
emits the variable names that are currently available
(within the present month) for the provided station identifier.

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    station: str = Field(
        ...,
        description="Station identifier to look for variables for.",
    )


@iemapp(
    memcachekey=lambda e: f"/json/dcp_vars|{e['station']}",
    content_type="application/json",
    help=__doc__,
    schema=Schema,
    memcacheexpire=3600,
)
def application(environ, start_response):
    """Answer request."""
    data = {
        "vars": [],
    }
    table = f"raw{utc():%Y_%m}"
    with get_sqlalchemy_conn("hads") as conn:
        res = conn.execute(
            text(
                f"""
            select distinct key from {table} where station = :station
        """
            ),
            {
                "station": environ["station"],
            },
        )
        for row in res:
            row = row._asdict()
            data["vars"].append(
                {
                    "id": row["key"],
                }
            )
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(data)
