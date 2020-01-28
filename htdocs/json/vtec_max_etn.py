"""Show Max ETNs by wfo, phenomena, sig, by year"""
import datetime
import json

import memcache
import pandas as pd
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def run(year, fmt):
    """Generate a report of max VTEC ETNs

    Args:
      year (int): year to run for
    """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    utcnow = datetime.datetime.utcnow()

    table = "warnings_%s" % (year,)
    cursor.execute(
        """
    SELECT wfo, phenomena, significance, max(eventid),
    '/vtec/#"""
        + str(year)
        + """-O-NEW-K'||
    wfo||'-'||phenomena||'-'||significance||'-'||
    LPAD(max(eventid)::text, 4, '0') as url
     from
    """
        + table
        + """ WHERE wfo is not null and eventid is not null and
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
    df.drop("max_eventid", axis=1, inplace=True)
    df = df.pivot_table(
        index="wfo",
        columns=["phenomena", "significance"],
        values="url",
        aggfunc=lambda x: " ".join(x),
    )
    df.fillna("", inplace=True)

    cls = ' class="table-bordered table-condensed table-striped"'
    html = ("<p><strong>Table generated at: %s</strong></p>\n%s") % (
        res["generated_at"],
        df.style.set_table_attributes(cls).render(),
    )
    return html


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)

    year = int(fields.get("year", 2015))
    fmt = fields.get("format", "json")
    if fmt not in ["json", "html"]:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        msg = "Invalid format provided."
        return [msg.encode("ascii")]
    cb = fields.get("callback", None)
    headers = []
    if fmt == "json":
        headers.append(("Content-type", "application/json"))
    else:
        headers.append(("Content-type", "text/html"))

    mckey = "/json/vtec_max_etn/%s/%s" % (year, fmt)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if res is None:
        res = run(year, fmt)
        mc.set(mckey, res, 3600)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    start_response("200 OK", headers)
    return [data.encode("ascii")]
