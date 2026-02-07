""".. title:: VTEC Max EventID by Year

Return to `JSON Services </json/>`_

Changelog
---------

- 2024-08-05: Initial documtation update

Example Requests
----------------

Provide all the max ETNs for 2024

https://mesonet.agron.iastate.edu/json/vtec_max_etn.py?year=2024&format=json

And as HTML

https://mesonet.agron.iastate.edu/json/vtec_max_etn.py?year=2024&format=html

"""

import json
from typing import Annotated

import pandas as pd
from pydantic import Field
from pyiem.database import get_dbconn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

from iemweb.util import get_ct


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="Optional JSONP callback function name")
    ] = None
    year: Annotated[int, Field(description="Year", ge=1986)] = 2015
    format: Annotated[
        str,
        Field(
            description="Format",
            pattern="json|html",
        ),
    ] = "json"


def run(year, fmt):
    """Generate a report of max VTEC ETNs

    Args:
      year (int): year to run for
    """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        """
    SELECT wfo, phenomena, significance, max(eventid),
    '/vtec/?year='||max(vtec_year)||'&wfo='||
    wfo||'&phenomena='||phenomena||'&significance='||significance||'&eventid='||
    max(eventid)::text
    from warnings WHERE vtec_year = %s and
    wfo is not null and eventid is not null and
    phenomena is not null and significance is not null
    GROUP by wfo, phenomena, significance
    ORDER by wfo ASC, phenomena ASC, significance ASC
    """,
        (year,),
    )
    res = {
        "count": cursor.rowcount,
        "generated_at": utc().strftime(ISO8601),
        "columns": [
            {"name": "wfo", "type": "str"},
            {"name": "phenomena", "type": "str"},
            {"name": "significance", "type": "str"},
            {"name": "max_eventid", "type": "int"},
            {"name": "url", "type": "str"},
        ],
        "table": cursor.fetchall(),
    }
    cursor.close()
    pgconn.close()

    if fmt == "json":
        return json.dumps(res)
    if not res["table"]:
        return "NO DATA"
    # Make a hacky table
    df = pd.DataFrame(
        res["table"], columns=[c["name"] for c in res["columns"]]
    )
    df["url"] = (
        '<a href="' + df["url"] + '">' + df["max_eventid"].apply(str) + "</a>"
    )
    df = (
        df.drop("max_eventid", axis=1)
        .pivot_table(
            index="wfo",
            columns=["phenomena", "significance"],
            values="url",
            aggfunc=" ".join,
        )
        .fillna("")
    )

    cls = ["table-bordered", "table-condensed", "table-striped"]
    html = (
        f"<p><strong>Table generated at: {res['generated_at']}</strong></p>\n"
        f"{df.to_html(classes=cls, escape=False)}"
    )
    return html


def get_mckey(environ):
    """Figure out the key."""
    year = environ["year"]
    fmt = environ["format"]
    return f"/json/vtec_max_etn/{year}/{fmt}"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type=get_ct,
    memcachekey=get_mckey,
    memcacheexpire=300,
)
def application(environ, start_response):
    """Answer request."""

    year = environ["year"]
    fmt = environ["format"]
    headers = [("Content-type", get_ct(environ))]

    res = run(year, fmt)
    start_response("200 OK", headers)
    return res
