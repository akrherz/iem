""".. title:: Example JSON Service

Return to `JSON Services </json/>`.

Example Requests
----------------

Just exercise the example.

https://mesonet.agron.iastate.edu/json/example.py

"""

import json

from pydantic import Field
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")


@iemapp(
    memcachekey="/json/example",
    content_type="application/json",
    help=__doc__,
    schema=Schema,
    memcacheexpire=0,
)
def application(_environ, start_response):
    """Answer request."""
    data = {
        "Name": "daryl",
        "Profession": "nerd",
        "Age": 99,
    }
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(data)
