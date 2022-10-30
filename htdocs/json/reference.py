"""pyIEM reference tables."""
import json

from pymemcache.client import Client
from paste.request import parse_formvars
from pyiem import reference
from pyiem.util import html_escape

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run():
    """Generate data."""
    return json.dumps({"prodDefinitions": reference.prodDefinitions})


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    cb = fields.get("callback", None)

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
