""".. title:: IEM Reference Data from pyIEM python library

Return to `API Services </api/#json>`_

Documentation for /json/reference.py
------------------------------------

This service simply exposes the reference data bundled within the
`pyIEM <https://github.com/akrherz/pyiem>`_ python library.  Not all fields
from the `pyiem.reference` namespace are exposed at the moment.

Changelog
---------

- 2025-02-28: Added VTEC Action, Phenomena, Significance reference data
- 2024-07-24: Initial documentation release

Example Usage
-------------

Return all reference data in JSON format.

https://mesonet.agron.iastate.edu/json/reference.py

"""

import json

from pydantic import Field
from pyiem import reference
from pyiem.nws.vtec import VTEC_ACTION, VTEC_PHENOMENA, VTEC_SIGNIFICANCE
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")


@iemapp(
    memcachekey="/json/reference/v3",
    help=__doc__,
    schema=Schema,
    memcacheexpire=86_400,
)
def application(_environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(
        {
            "prodDefinitions": reference.prodDefinitions,
            "vtec_action": VTEC_ACTION,  # should have been status, sigh
            "vtec_phenomena": VTEC_PHENOMENA,
            "vtec_significance": VTEC_SIGNIFICANCE,
        }
    )
