"""
 Aggregate the RIDGE current files
"""
import datetime
import glob
import json

from pyiem.reference import ISO8601
from pyiem.util import LOG, html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run(product):
    """Actually run for this product"""

    res = {
        "generation_time_utc": datetime.datetime.utcnow().strftime(ISO8601),
        "product": product,
        "meta": [],
    }

    for fn in glob.glob(
        f"/mesonet/ldmdata/gis/images/4326/ridge/???/{product}_0.json"
    ):
        try:
            with open(fn, encoding="utf-8") as fh:
                j = json.load(fh)
            res["meta"].append(j["meta"])
        except Exception as exp:
            LOG.info(exp)

    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    product = environ.get("product", "N0B")[:3].upper()
    cb = environ.get("callback", None)

    mckey = f"/json/ridge_current_{product}.json"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(product)
        mc.set(mckey, res, 30)
    else:
        res = res.decode("ascii")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
