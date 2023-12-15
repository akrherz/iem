"""
 Tile Map service metadata
"""
import datetime
import json
import os

from pyiem.reference import ISO8601
from pyiem.util import html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run():
    """Generate json response"""
    res = {
        "generation_utc_time": datetime.datetime.utcnow().strftime(ISO8601),
        "services": [],
    }
    fn = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json"
    if not os.path.isfile(fn):
        return "ERROR"
    with open(fn, encoding="utf-8") as fh:
        j = json.load(fh)
    vt = datetime.datetime.strptime(j["meta"]["valid"], ISO8601)
    res["services"].append(
        {
            "id": "ridge_uscomp_n0q",
            "layername": f"ridge::USCOMP-N0Q-{vt:%Y%m%d%H%M}",
            "utc_valid": j["meta"]["valid"],
        }
    )
    fn = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.json"
    with open(fn, encoding="utf-8") as fh:
        j = json.load(fh)
    vt = datetime.datetime.strptime(j["meta"]["valid"], ISO8601)
    res["services"].append(
        {
            "id": "ridge_uscomp_n0r",
            "layername": f"ridge::USCOMP-N0R-{vt:%Y%m%d%H%M}",
            "utc_valid": j["meta"]["valid"],
        }
    )

    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    if environ["REQUEST_METHOD"] not in ["GET", "POST"]:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        data = "Invalid Request"
        return [data.encode("ascii")]

    cb = environ.get("callback")

    mckey = "/json/tms.json"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if res is None:
        res = run()
        mc.set(mckey, res, 15)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
