""".. title:: NWS Text Data by Center and Date

Return to `JSON Services </json/>`_

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

# stdlib
import json
from datetime import datetime, timedelta

from pydantic import AwareDatetime, Field
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        None, description="Optional JSONP callback function name"
    )
    date: str = Field(
        None,
        description="Optional date to limit the search to, YYYY-MM-DD",
        pattern=r"\d{4}-\d{1,2}-\d{1,2}",
    )
    center: str = Field(
        default="KOKX",
        description="NWS Center Identifier (4 character)",
        min_length=4,
        max_length=4,
    )
    opt: bool = Field(
        False, description="Optional flag to limit to certain product types"
    )
    sts: AwareDatetime = Field(
        None,
        description="Optional start time for the search",
    )
    ets: AwareDatetime = Field(
        None,
        description="Optional end time for the search",
    )


@iemapp(help=__doc__, schema=Schema, default_tz="UTC", iemdb="afos")
def application(environ, start_response):
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
    if environ["opt"]:
        pil_limiter = """
            and substr(pil, 1, 3) in ('AQA', 'CFW', 'DGT', 'DSW', 'FFA',
            'FFS', 'FFW', 'FLS', 'FLW', 'FWW', 'HLS', 'MWS', 'MWW', 'NPW',
            'NOW', 'PNS', 'PSH', 'RER', 'RFW', 'RWR', 'RWS', 'SMW', 'SPS',
            'SRF', 'SQW', 'SVR', 'SVS', 'TCV', 'TOR', 'TSU', 'WCN', 'WSW')
        """

    environ["iemdb.afos.cursor"].execute(
        "SELECT data, to_char(entered at time zone 'UTC', "
        "'YYYY-MM-DDThh24:MI:00Z') as ee from products "
        "where source = %s and entered >= %s and "
        f"entered < %s {pil_limiter} ORDER by entered ASC",
        (center, environ["sts"], environ["ets"]),
    )
    for row in environ["iemdb.afos.cursor"]:
        root["products"].append({"data": row["data"], "entered": row["ee"]})

    data = json.dumps(root)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return data.encode("ascii")
