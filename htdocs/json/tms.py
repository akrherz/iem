"""
 Tile Map service metadata
"""
import json
import os
import datetime

import memcache
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
    j = json.load(open(fn))
    vt = datetime.datetime.strptime(j["meta"]["valid"], iso)
    res["services"].append(
        {
            "id": "ridge_uscomp_n0q",
            "layername": "ridge::USCOMP-N0Q-%s" % vt.strftime("%Y%m%d%H%M"),
            "utc_valid": j["meta"]["valid"],
        }
    )

    j = json.load(open("/mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.json"))
    vt = datetime.datetime.strptime(j["meta"]["valid"], iso)
    res["services"].append(
        {
            "id": "ridge_uscomp_n0r",
            "layername": "ridge::USCOMP-N0R-%s" % vt.strftime("%Y%m%d%H%M"),
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
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 15)
    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
