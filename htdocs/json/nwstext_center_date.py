"""
Provide nws text for one center for one date.
"""
# stdlib
import datetime
import json

# extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape, utc


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor()
    center = fields.get("center", "KOKX")[:4]
    cb = fields.get("callback")
    date = datetime.datetime.strptime(
        fields.get("date", "2020-03-15"), "%Y-%m-%d"
    )
    sts = utc(date.year, date.month, date.day)
    ets = sts + datetime.timedelta(days=1)
    root = {"products": []}
    pil_limiter = ""
    if int(fields.get("opt", 0)) == 1:
        pil_limiter = """
            and substr(pil, 1, 3) in ('AQA', 'CFW', 'DGT', 'FFA',
            'FFS', 'FFW', 'FLS', 'FLW', 'HLS', 'MWS', 'MWW', 'NPW', 'NOW',
            'PNS', 'PSH', 'RER', 'RFW', 'RWR', 'RWS', 'SMW', 'SPS', 'SRF',
            'SVR', 'SVS', 'TOR', 'WCN', 'WSW') """

    acursor.execute(
        """
        SELECT data from products where source = %s and
        entered >= %s and entered < %s """
        + pil_limiter
        + """
        ORDER by entered ASC
        """,
        (center, sts, ets),
    )
    for row in acursor:
        root["products"].append({"data": row[0]})

    if cb is None:
        data = json.dumps(root)
    else:
        data = "%s(%s)" % (html_escape(cb), json.dumps(root))

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
