"""
Search for NWS Text, return JSON
"""

import datetime
import json

from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconn, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run(sts, ets, awipsid):
    """Actually do some work!"""
    dbconn = get_dbconn("afos")
    cursor = dbconn.cursor()

    res = {"results": []}
    pillimit = "pil"
    if len(awipsid) == 3:
        pillimit = "substr(pil, 1, 3) "
    cursor.execute(
        f"""
    SELECT data,
    to_char(entered at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ'),
    source, wmo from products WHERE
    entered >= %s and entered < %s and {pillimit} = %s
    ORDER by entered ASC
    """,
        (sts, ets, awipsid),
    )
    for row in cursor:
        res["results"].append(
            dict(ttaaii=row[3], utcvalid=row[1], data=row[0], cccc=row[2])
        )
    return json.dumps(res)


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Answer request."""
    if "sts" not in environ:
        raise IncompleteWebRequest("No sts provided")
    headers = [("Content-type", "application/json")]
    if environ.get("REQUEST_METHOD") != "GET":
        start_response("405 Method Not Allowed", headers)
        return ['{"error": "Only HTTP GET Supported"}'.encode("utf8")]
    awipsid = environ.get("awipsid", "AFDDMX")[:6]
    cb = environ.get("callback", None)

    mckey = (
        f"/json/nwstext_search/{environ['sts']:%Y%m%d%H%M}/"
        f"{environ['ets']:%Y%m%d%H%M}/{awipsid}?callback={cb}"
    )
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=datetime.timezone.utc)
        cacheexpire = 0 if environ["ets"] < now else 120

        res = run(environ["sts"], environ["ets"], awipsid)
        mc.set(mckey, res, cacheexpire)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    start_response("200 OK", headers)
    return [res.encode("ascii")]
