"""
Provide nws text for one center for one date, or not.
"""
# stdlib
import json
from datetime import datetime, timedelta

# extras
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconn, html_escape, utc
from pyiem.webutil import iemapp


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Answer request."""
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor()
    center = environ.get("center", "KOKX")[:4]
    cb = environ.get("callback")
    if environ.get("date") is not None:
        date = datetime.strptime(environ.get("date", "2020-03-15"), "%Y-%m-%d")
        environ["sts"] = utc(date.year, date.month, date.day)
        environ["ets"] = environ["sts"] + timedelta(days=1)
    else:
        if environ.get("sts") is None:
            raise IncompleteWebRequest("No date information provided")
        if (environ["ets"] - environ["sts"]) > timedelta(days=14):
            environ["ets"] = environ["sts"] + timedelta(days=14)

    root = {"products": []}
    pil_limiter = ""
    if int(environ.get("opt", 0)) == 1:
        pil_limiter = """
            and substr(pil, 1, 3) in ('AQA', 'CFW', 'DGT', 'DSW', 'FFA',
            'FFS', 'FFW', 'FLS', 'FLW', 'FWW', 'HLS', 'MWS', 'MWW', 'NPW',
            'NOW', 'PNS', 'PSH', 'RER', 'RFW', 'RWR', 'RWS', 'SMW', 'SPS',
            'SRF', 'SQW', 'SVR', 'SVS', 'TCV', 'TOR', 'TSU', 'WCN', 'WSW')
        """

    acursor.execute(
        "SELECT data, to_char(entered at time zone 'UTC', "
        "'YYYY-MM-DDThh24:MI:00Z') from products "
        "where source = %s and entered >= %s and "
        f"entered < %s {pil_limiter} ORDER by entered ASC",
        (center, environ["sts"], environ["ets"]),
    )
    for row in acursor:
        root["products"].append({"data": row[0], "entered": row[1]})

    data = json.dumps(root)
    if cb is not None:
        data = f"{html_escape(cb)}({data})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
