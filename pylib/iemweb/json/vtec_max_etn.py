"""Show Max ETNs by wfo, phenomena, sig, by year"""

import json

import pandas as pd
from pydantic import Field
from pyiem.database import get_dbconn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(default=None, title="JSONP Callback")
    year: int = Field(default=2015, title="Year")
    format: str = Field(default="json", title="Format", pattern="json|html")


def run(year, fmt):
    """Generate a report of max VTEC ETNs

    Args:
      year (int): year to run for
    """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute(
        f"""
    SELECT wfo, phenomena, significance, max(eventid),
    '/vtec/#{year}-O-NEW-K'||
    wfo||'-'||phenomena||'-'||significance||'-'||
    LPAD(max(eventid)::text, 4, '0') as url
     from warnings_{year} WHERE wfo is not null and eventid is not null and
    phenomena is not null and significance is not null
    GROUP by wfo, phenomena, significance
    ORDER by wfo ASC, phenomena ASC, significance ASC
    """
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


def get_ct(environ):
    """Figure out the content type."""
    fmt = environ["format"]
    if fmt == "json":
        return "application/json"
    return "text/html"


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
    headers = [
        ("Content-type", get_ct(environ)),
    ]

    res = run(year, fmt)
    start_response("200 OK", headers)
    return res
