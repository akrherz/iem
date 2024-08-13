""".. title:: Recent IEM Station Metadata Changes

Return to `JSON Services </json/>`_

This service emits station metadata for those stations that have recently
received updates by the IEM.  There is a 1000 result limit to what is returned.

Changelog
---------

- 2024-08-12: Initial documentation update

Example Requests
----------------

Return the metadata for stations with a metadata change done today.

https://mesonet.agron.iastate.edu/json/stations.py

"""

import datetime
import json

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    date: datetime.date = Field(
        default=datetime.date.today(),
        description="Query metadata changes since this date.",
    )


def run(dt):
    """Actually run for this product"""

    data = {
        "generated_at": utc().strftime(ISO8601),
    }
    with get_sqlalchemy_conn("mesosite") as conn:
        changed = pd.read_sql(
            text(
                "select *, st_x(geom) as lon, st_y(geom) as lat from "
                "stations where modified > :dt ORDER by modified DESC "
                "limit 1000"
            ),
            conn,
            params={"dt": dt},
            parse_dates=["modified", "archive_begin", "archive_end"],
        )
    # Eh, ensure state is not null
    changed["state"] = changed["state"].fillna("")
    # Convert timestamps to strings
    changed["modified"] = changed["modified"].dt.strftime(ISO8601)
    changed["archive_begin"] = changed["archive_begin"].dt.strftime("%Y-%m-%d")
    changed["archive_end"] = changed["archive_end"].dt.strftime("%Y-%m-%d")
    data["stations"] = changed.drop(columns="geom").to_dict(orient="records")
    return json.dumps(data).replace("NaN", "null")


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type="application/json",
    memcachekey=lambda x: f"/json/stations.py|{x['date']}",
    memcacheexpire=300,
)
def application(environ, start_response):
    """Answer request."""
    res = run(environ["date"])
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
