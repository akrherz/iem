""".. title:: Search for NWS Text Products over a time range

Return to `JSON Services </json/>`_

Documentation for /json/nwstext_search.py
-----------------------------------------

This legacy service returns a JSON response of NWS Text Products over a time
range.

Changelog
---------

- 2024-07-25: Initial documentation

Example Usage
-------------

Return all Des Moines Area Forecast Discussions for 2024

https://mesonet.agron.iastate.edu/json/nwstext_search.py?awipsid=AFDDMX&\
sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z

Return all Severe Thunderstorm Warnings for 10 July 2024 UTC

https://mesonet.agron.iastate.edu/json/nwstext_search.py?awipsid=SVR&\
sts=2024-07-10T00:00Z&ets=2024-07-11T00:00Z

"""

import datetime
import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    awipsid: str = Field(
        "AFDDMX",
        description="The AWIPS Identifier to search for",
        max_length=6,
        min_length=3,
    )
    sts: datetime.datetime = Field(
        ..., description="Start of the time period (UTC) to search for"
    )
    ets: datetime.datetime = Field(
        ..., description="End of the time period (UTC) to search for"
    )


def run(sts, ets, awipsid):
    """Actually do some work!"""

    data = {"results": []}
    pillimit = "pil"
    if len(awipsid) == 3:
        pillimit = "substr(pil, 1, 3) "
    with get_sqlalchemy_conn("afos") as conn:
        res = conn.execute(
            text(f"""
        SELECT data,
        to_char(entered at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ'),
        source, wmo from products WHERE
        entered >= :sts and entered < :ets and {pillimit} =:awipsid
        ORDER by entered ASC
        """),
            {"sts": sts, "ets": ets, "awipsid": awipsid},
        )
        for row in res:
            data["results"].append(
                dict(ttaaii=row[3], utcvalid=row[1], data=row[0], cccc=row[2])
            )
    return json.dumps(data)


def get_mckey(environ: dict) -> str:
    """Get the key."""
    return (
        f"/json/nwstext_search/{environ['sts']:%Y%m%d%H%M}/"
        f"{environ['ets']:%Y%m%d%H%M}/{environ['awipsid']}"
    ).replace(" ", "")


@iemapp(
    help=__doc__,
    memcachekey=get_mckey,
    memcacheexpire=120,
    schema=Schema,
    default_tz="UTC",
)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]

    res = run(environ["sts"], environ["ets"], environ["awipsid"])
    start_response("200 OK", headers)
    return res.encode("ascii")
