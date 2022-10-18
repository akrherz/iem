"""
 Tile Map service metadata
"""
import json
import os
import datetime

from pymemcache.client import Client
from paste.request import parse_formvars
from pyiem.util import html_escape


def run():
    """Generate json response"""
    iso = "%Y-%m-%dT%H:%M:%SZ"
    res = {
        "generation_utc_time": datetime.datetime.utcnow().strftime(iso),
        "services": [],
    }
    fn = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json"
    if not os.path.isfile(fn):
        return "ERROR"
    with open(fn, encoding="utf-8") as fh:
        j = json.load(fh)
    vt = datetime.datetime.strptime(j["meta"]["valid"], iso)
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
    vt = datetime.datetime.strptime(j["meta"]["valid"], iso)
    res["services"].append(
        {
            "id": "ridge_uscomp_n0r",
            "layername": f"ridge::USCOMP-N0R-{vt:%Y%m%d%H%M}",
            "utc_valid": j["meta"]["valid"],
        }
    )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    if environ["REQUEST_METHOD"] not in ["GET", "POST"]:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        data = "Invalid Request"
        return [data.encode("ascii")]

    cb = fields.get("callback")

    mckey = "/json/tms.json"
    mc = Client("iem-memcached.local:11211")
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
