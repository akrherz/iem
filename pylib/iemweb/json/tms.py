""".. title:  IEM Tile Map Service metadata

Return to `API Services </api/#json>`_

Documentation for /json/tms.json
--------------------------------

This service provides a JSON response that describes the Tile Map Services
(TMS) available from the IEM.

Changelog
---------

- 2026-03-04: Renamed `generation_utc_time` to `generated_at` to provide better
  IEM webservice consistency.
- 2024-08-12: Initial documentation update.

Example Usage
-------------

Nothing much for configuration, just call the service.

https://mesonet.agron.iastate.edu/json/tms.json

"""

import json
import os
from datetime import datetime

from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import CALLBACK_FIELD
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None


def run():
    """Generate json response"""
    res = json_response_dict(
        {
            "services": [],
        }
    )
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
def application(_environ: dict, start_response: callable):
    """Answer request."""
    res = run()
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
