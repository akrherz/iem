""" Find VTEC events by a given UGC code. """
import json
import datetime

from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape
from pandas.io.sql import read_sql


def run(ugc, sdate, edate):
    """ Answer the request! """
    pgconn = get_dbconn("postgis")

    df = read_sql(
        """
        SELECT
        to_char(issue at time zone 'UTC',
            'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
        to_char(expire at time zone 'UTC',
            'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
        eventid, phenomena, significance, hvtec_nwsli, wfo
        from warnings WHERE ugc = %s and issue > %s
        and issue < %s ORDER by issue ASC
        """,
        pgconn,
        params=(ugc, sdate, edate),
    )

    res = {"events": []}
    for _, row in df.iterrows():
        res["events"].append(
            {
                "issue": row["iso_issued"],
                "expire": row["iso_expired"],
                "eventid": row["eventid"],
                "phenomena": row["phenomena"],
                "hvtec_nwsli": row["hvtec_nwsli"],
                "significance": row["significance"],
                "wfo": row["wfo"],
            }
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    ugc = fields.get("ugc", "IAC001")[:6]
    sdate = datetime.datetime.strptime(
        fields.get("sdate", "1986/1/1"), "%Y/%m/%d"
    )
    edate = datetime.datetime.strptime(
        fields.get("edate", "2099/1/1"), "%Y/%m/%d"
    )
    cb = fields.get("callback", None)

    res = run(ugc, sdate, edate)
    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
