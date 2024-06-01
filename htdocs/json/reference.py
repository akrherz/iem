"""pyIEM reference tables."""

import json

from pydantic import Field
from pyiem import reference
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")


@iemapp(
    memcachekey="/json/reference/v2",
    help=__doc__,
    schema=Schema,
    memcacheexpire=0,
)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps({"prodDefinitions": reference.prodDefinitions})
