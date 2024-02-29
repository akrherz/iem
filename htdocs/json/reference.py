"""pyIEM reference tables."""

import json

from pyiem import reference
from pyiem.util import html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def run():
    """Generate data."""
    return json.dumps({"prodDefinitions": reference.prodDefinitions})


@iemapp()
def application(environ, start_response):
    """Answer request."""
    cb = environ.get("callback", None)

    mckey = "/json/reference/v2"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 0)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
