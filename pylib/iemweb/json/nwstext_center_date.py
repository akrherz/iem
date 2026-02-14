""".. title:: NWS Text Data by Center and Date

Return to `API Services </api/#json>`_

Documentation for /json/nwstext_center_date.py
----------------------------------------------

This service returns NWS Text data for a given center and date.

Changelog
---------

- 2024-07-26: Initial documentation release and pydantic validation

Example Requests
----------------

Return most all NWS Des Moines products for 2024-07-15:

https://mesonet.agron.iastate.edu/json/nwstext_center_date.py?center=KDMX\
&date=2024-07-15&opt=1

Return products from NWS Des Moines for 2 day period:

https://mesonet.agron.iastate.edu/json/nwstext_center_date.py?center=KDMX\
&sts=2024-07-15T00:00Z&ets=2024-07-17T00:00Z

"""

import json
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

OPTPILS = (
    "AQA CFW DGT DSW FFA FFS FFW FLS FLW FWW HLS MWS MWW NPW NOW PNS PSH RER "
    "RFW RWR RWS SMW SPS SRF SQW SVR SVS TCV TOR TSU WCN WSW"
).split()


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="Optional JSONP callback function name")
    ] = None
    date: Annotated[
        str | None,
        Field(
            description="Optional date to limit the search to, YYYY-MM-DD",
            pattern=r"\d{4}-\d{1,2}-\d{1,2}",
        ),
    ] = None
    center: Annotated[
        str,
        Field(
            description="NWS Center Identifier (4 character)",
            min_length=4,
            max_length=4,
        ),
    ] = "KOKX"
    opt: Annotated[
        bool,
        Field(
            description=(
                "Optional flag to limit to certain pil "
                f"types {', '.join(OPTPILS)}"
            ),
        ),
    ] = False
    sts: Annotated[
        AwareDatetime | None,
        Field(
            description="Optional start time for the search",
        ),
    ] = None
    ets: Annotated[
        AwareDatetime,
        Field(
            description="Optional end time for the search",
        ),
    ] = None


@iemapp(help=__doc__, schema=Schema, default_tz="UTC")
def application(environ: dict, start_response: callable):
    """Answer request."""
    center = environ["center"]
    if environ["date"] is not None:
        date = datetime.strptime(environ["date"], "%Y-%m-%d")
        environ["sts"] = utc(date.year, date.month, date.day)
        environ["ets"] = environ["sts"] + timedelta(days=1)
    else:
        if environ["sts"] is None or environ["ets"] is None:
            raise IncompleteWebRequest("No date information provided")
        if (environ["ets"] - environ["sts"]) > timedelta(days=14):
            environ["ets"] = environ["sts"] + timedelta(days=14)

    root = {"products": []}
    pil_limiter = ""
    params = {
        "center": center,
        "sts": environ["sts"],
        "ets": environ["ets"],
    }
    if environ["opt"]:
        params["pils"] = OPTPILS
        pil_limiter = "and substr(pil, 1, 3) = ANY(:pils) "
    with get_sqlalchemy_conn("afos") as conn:
        res = conn.execute(
            sql_helper(
                """
                SELECT data, to_char(entered at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:00Z') as e from products
                where source = :center and entered >= :sts and entered < :ets
                {pil_limiter} ORDER by entered ASC
            """,
                pil_limiter=pil_limiter,
            ),
            params,
        )
        for row in res:
            root["products"].append({"data": row.data, "entered": row.e})

    data = json.dumps(root)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return data.encode("ascii")
