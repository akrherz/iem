""".. title:: QR Code Generator

Generate a QR code for a given query string.

Example Usage
-------------

https://mesonet.agron.iastate.edu/plotting/auto/gen_qrcode.py?\
q=network:WFO::wfo:DMX::var:tmpf::year1:2023::month1:5::day1:1::hour1&p=1

"""

import hashlib
from io import BytesIO
from typing import Annotated

import qrcode
from pydantic import Field
from pyiem.webutil import CGIModel, iemapp
from pymemcache.client import Client

HTTP200 = "200 OK"


class MyModel(CGIModel):
    p: Annotated[
        str | None,
        Field(
            title="Plot Type",
            description="The plot type to use, if any",
        ),
    ] = None
    q: Annotated[
        str,
        Field(
            title="Query String",
            description="The query string to encode in the QR code.",
            min_length=1,
            max_length=2048,
        ),
    ]


def q2uri(qstr: str, pval: str):
    """Convert the query string to a URI."""
    if qstr.startswith("https://mesonet"):
        return qstr
    uri = "https://mesonet.agron.iastate.edu/plotting/auto/?"
    if pval is not None:
        uri += f"q={pval}&"
    for token in qstr.split("::"):
        token2 = token.split(":")
        if len(token2) != 2:
            continue
        uri += f"{token2[0]}={token2[1]}&"
    return uri[:-1]


@iemapp(help=__doc__, schema=MyModel)
def application(environ: dict, start_response):
    """Our Application!"""
    qstr = environ["q"]
    if qstr.find("network:WFO::wfo:PHEB") > -1:
        qstr = qstr.replace("network:WFO", "network:NWS")
    if qstr.find("network:WFO::wfo:PAAQ") > -1:
        qstr = qstr.replace("network:WFO", "network:NWS")
    uri = q2uri(qstr, environ["p"])
    mckey = hashlib.sha256(uri.encode("utf-8")).hexdigest()
    # Figure out what our response headers should be
    response_headers = [("Content-type", "image/png")]
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        img = qrcode.make(uri)
        bio = BytesIO()
        img.save(bio, "PNG")
        res = bio.getvalue()
        bio.close()
        mc.set(mckey, res, 0)
    mc.close()
    start_response(HTTP200, response_headers)
    return [res]
