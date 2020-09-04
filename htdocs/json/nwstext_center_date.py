"""
Provide nws text for one center for one date, or not.
"""
# stdlib
from datetime import timezone, datetime, timedelta
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
    if fields.get("date") is not None:
        date = datetime.strptime(fields.get("date", "2020-03-15"), "%Y-%m-%d")
        sts = utc(date.year, date.month, date.day)
        ets = sts + timedelta(days=1)
    else:
        sts = datetime.strptime(
            fields.get("sts", "2020-03-15T00:00")[:16], "%Y-%m-%dT%H:%M"
        )
        ets = datetime.strptime(
            fields.get("ets", "2020-03-16T00:00")[:16], "%Y-%m-%dT%H:%M"
        )
        if (ets - sts) > timedelta(days=14):
            ets = sts + timedelta(days=14)
        sts = sts.replace(tzinfo=timezone.utc)
        ets = ets.replace(tzinfo=timezone.utc)

    root = {"products": []}
    pil_limiter = ""
    if int(fields.get("opt", 0)) == 1:
        pil_limiter = """
            and substr(pil, 1, 3) in ('AQA', 'CFW', 'DGT', 'DSW', 'FFA',
            'FFS', 'FFW', 'FLS', 'FLW', 'FWW', 'HLS', 'MWS', 'MWW', 'NPW',
            'NOW', 'PNS', 'PSH', 'RER', 'RFW', 'RWR', 'RWS', 'SMW', 'SPS',
            'SRF', 'SQW', 'SVR', 'SVS', 'TCV', 'TOR', 'TSU', 'WCN', 'WSW')
        """

    acursor.execute(
        "SELECT data from products where source = %s and entered >= %s and "
        f"entered < %s {pil_limiter} ORDER by entered ASC",
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
