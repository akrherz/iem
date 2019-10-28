#!/usr/bin/env python
"""
 Aggregate the RIDGE current files
"""
import json
import datetime
import glob

import memcache
from paste.request import parse_formvars
from pyiem.util import html_escape

ISO = "%Y-%m-%dT%H:%M:%SZ"


def run(product):
    """ Actually run for this product """

    res = {
        "generation_time_utc": datetime.datetime.utcnow().strftime(ISO),
        "product": product,
        "meta": [],
    }

    for fn in glob.glob(
        ("/home/ldm/data/gis/images/4326/" "ridge/???/%s_0.json") % (product,)
    ):
        try:
            j = json.load(open(fn))
            res["meta"].append(j["meta"])
        except Exception:
            pass

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    product = fields.get("product", "N0Q")[:3].upper()
    cb = fields.get("callback", None)

    mckey = "/json/ridge_current_%s.json" % (product,)
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(product)
        mc.set(mckey, res, 30)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
