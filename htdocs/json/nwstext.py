#!/usr/bin/env python
"""
Provide nws text in JSON format
"""
# stdlib
import datetime
import json

# extras
import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    pgconn = get_dbconn("afos")
    acursor = pgconn.cursor()
    pid = fields.get("product_id", "201302241937-KSLC-NOUS45-PNSSLC")
    cb = fields.get("callback")
    utc = datetime.datetime.strptime(pid[:12], "%Y%m%d%H%M")
    utc = utc.replace(tzinfo=pytz.UTC)
    pil = pid[-6:]
    root = {"products": []}

    acursor.execute(
        """
        SELECT data from products where pil = %s and
        entered = %s
        """,
        (pil, utc),
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
