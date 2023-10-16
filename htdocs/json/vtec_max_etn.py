"""Show Max ETNs by wfo, phenomena, sig, by year"""
import datetime
import json

import pandas as pd
from pyiem.util import get_dbconn, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run(year, fmt):
    """Generate a report of max VTEC ETNs

    Args:
      year (int): year to run for
    """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    utcnow = datetime.datetime.utcnow()

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
        "generated_at": utcnow.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "columns": [
            {"name": "wfo", "type": "str"},
            {"name": "phenomena", "type": "str"},
            {"name": "significance", "type": "str"},
            {"name": "max_eventid", "type": "int"},
            {"name": "url", "type": "str"},
        ],
        "table": cursor.fetchall(),
    }

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


@iemapp()
def application(environ, start_response):
    """Answer request."""

    year = int(environ.get("year", 2015))
    fmt = environ.get("format", "json")
    if fmt not in ["json", "html"]:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        msg = "Invalid format provided."
        return [msg.encode("ascii")]
    cb = environ.get("callback", None)
    headers = []
    if fmt == "json":
        headers.append(("Content-type", "application/json"))
    else:
        headers.append(("Content-type", "text/html"))

    mckey = f"/json/vtec_max_etn/{year}/{fmt}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if res is None:
        res = run(year, fmt)
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
