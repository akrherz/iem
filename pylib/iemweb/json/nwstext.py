""".. title:: Single Instance NWS Text Product JSON Service

Return to `JSON Services </json/>`_

Documentation for /json/nwstext.py
----------------------------------

Note: This is a legacy service that should not be used for new development.
The `CGI version </cgi-bin/afos/retrieve.py?help>`_ is the preferred method
at the moment.  This service does do a needed job of returning multiple
product texts for a single product identifier, which is sadly still a thing
in the world of NWS text products.

This service requires that you know the ``product_id`` ahead of time.  This is
an identifier created by the IEM attempting to uniquely identify a text
product.

Changelog
---------

- 2024-07-26: Initial documentation Release

Example Usage
-------------

Return the Area Forecast Discussion for NWS Des Moines issued at 2024-07-16
04:52 UTC:

https://mesonet.agron.iastate.edu/json/nwstext.py?\
product_id=202407160452-KDMX-FXUS63-AFDDMX

"""

# stdlib
import datetime
import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        None, description="Optional JSONP callback function name"
    )
    product_id: str = Field(
        ...,
        description="Product Identifier to retrieve text for",
        max_length=36,
        min_length=28,
        pattern=r"^\d{12}-[A-Z0-9]{4}-[A-Z0-9]{6}-[A-Z0-9]{3,6}$",
    )


@iemapp(
    help=__doc__,
    memcachekey=lambda x: f"/json/nwstext|{x['product_id']}",
    memcacheexpire=300,
    schema=Schema,
)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]

    pid = environ["product_id"]
    tokens = pid.split("-")
    utc = datetime.datetime.strptime(tokens[0], "%Y%m%d%H%M")
    utc = utc.replace(tzinfo=datetime.timezone.utc)
    root = {"products": []}

    with get_sqlalchemy_conn("afos") as conn:
        res = conn.execute(
            text(
                "SELECT data from products "
                "where pil = :pil and entered = :entered"
            ),
            {"pil": tokens[3], "entered": utc},
        )
        for row in res:
            root["products"].append({"data": row[0]})

    data = json.dumps(root)
    start_response("200 OK", headers)
    return data.encode("ascii")
