"""Generate QR codes on-the-fly."""
# stdlib
import hashlib
from io import BytesIO

# third party
from paste.request import parse_formvars
from pymemcache.client import Client
import qrcode

HTTP200 = "200 OK"


def q2uri(qstr, pval):
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


def application(environ, start_response):
    """Our Application!"""
    fields = parse_formvars(environ)
    # HACK
    if fields.get("q", "").find("network:WFO::wfo:PHEB") > -1:
        fields["q"] = fields["q"].replace("network:WFO", "network:NWS")
    if fields.get("q", "").find("network:WFO::wfo:PAAQ") > -1:
        fields["q"] = fields["q"].replace("network:WFO", "network:NWS")
    uri = q2uri(fields.get("q"), fields.get("p"))
    mckey = hashlib.md5(uri.encode("utf-8")).hexdigest()
    # Figure out what our response headers should be
    response_headers = [("Content-type", "image/png")]
    mc = Client(["iem-memcached", 11211])
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
