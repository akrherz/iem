""".. title:  IEM Tile Map Service metadata

Return to `API Services </api/#json>`_

Documentation for /json/tms.json
--------------------------------

This service provides a JSON response that describes the Tile Map Services
(TMS) available from the IEM.

Changelog
---------

- 2024-08-12: Initial documentation update.

Example Usage
-------------

Nothing much for configuration, just call the service.

https://mesonet.agron.iastate.edu/json/tms.json

"""

import json
import os
from datetime import datetime

from pydantic import Field
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")


def run():
    """Generate json response"""
    res = {
        "generation_utc_time": utc().strftime(ISO8601),
        "services": [],
    }
    fn = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.json"
    if not os.path.isfile(fn):
        return "ERROR"
    with open(fn, encoding="utf-8") as fh:
        j = json.load(fh)
    vt = datetime.strptime(j["meta"]["valid"], ISO8601)
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
    vt = datetime.strptime(j["meta"]["valid"], ISO8601)
    res["services"].append(
        {
            "id": "ridge_uscomp_n0r",
            "layername": f"ridge::USCOMP-N0R-{vt:%Y%m%d%H%M}",
            "utc_valid": j["meta"]["valid"],
        }
    )

    return json.dumps(res)


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey="/json/tms.json",
    memcacheexpire=15,
)
def application(environ, start_response):
    """Answer request."""
    if environ["REQUEST_METHOD"] not in ["GET", "POST"]:
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        data = "Invalid Request"
        return [data.encode("ascii")]

    res = run()
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
