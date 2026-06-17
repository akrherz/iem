""".. title:: Single Product NWS Text Product JSON Service

Return to `API Services </api/#json>`_

Documentation for /json/nwstext.py
----------------------------------

Note: This is a legacy service that should not be used for new development.
The `CGI version </cgi-bin/afos/retrieve.py?help>`_ is the preferred method
at the moment.  This service does do a needed job of returning multiple
product texts for a single product identifier, which is sadly still a thing
in the world of NWS text products.

This service requires that you know the ``product_id`` ahead of time.  This is
an identifier created by the IEM attempting to uniquely identify a text
product.  This ``product_id`` is a dash delimited string seperating a
UTC timestamp, WMO source, WMO TTAAII, AWIPS ID, and an optional BBB field.

Changelog
---------

- 2026-05-08: Service updated to support the bbb field of a product identifier,
  if not provided, the service does not use it in the database query.
- 2024-07-26: Initial documentation Release

Example Usage
-------------

Return the Area Forecast Discussion for NWS Des Moines issued at 2024-07-16
04:52 UTC:

https://mesonet.agron.iastate.edu/json/nwstext.py?\
product_id=202407160452-KDMX-FXUS63-AFDDMX

"""

import json
from datetime import datetime, timezone
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import BadWebRequest
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import CALLBACK_FIELD
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    product_id: Annotated[
        str,
        Field(
            description="Product Identifier to retrieve text for",
            max_length=36,
            min_length=28,
            pattern=(
                r"^\d{12}-[A-Z0-9]{4}-[A-Z0-9]{6}-[A-Z0-9]{3,6}"
                r"(?:-[A-Z0-9]{3})?$"
            ),
        ),
    ]


@iemapp(
    help=__doc__,
    memcachekey=lambda x: f"/json/nwstext|{x['product_id']}",
    memcacheexpire=300,
    schema=Schema,
)
def application(environ: dict, start_response: callable):
    """Answer request."""
    pid = environ["product_id"]
    tokens = pid.split("-")
    try:
        utc = datetime.strptime(tokens[0], "%Y%m%d%H%M")
    except ValueError as exp:
        raise BadWebRequest("Invalid timestamp") from exp
    utc = utc.replace(tzinfo=timezone.utc)
    root = json_response_dict({"products": []})

    sql_bbb = ""
    if len(tokens) > 4 and tokens[4] != "":
        sql_bbb = "and bbb is not distinct from :bbb"
    with get_sqlalchemy_conn("afos") as conn:
        res = conn.execute(
            sql_helper(
                "SELECT data from products "
                "where pil = :pil and entered = :entered"
                " {sql_bbb}",
                sql_bbb=sql_bbb,
            ),
            {
                "pil": tokens[3],
                "entered": utc,
                "bbb": tokens[4] if len(tokens) > 4 else None,
            },
        )
        for row in res:
            root["products"].append({"data": row[0]})

    data = json.dumps(root)
    start_response("200 OK", [("Content-type", "application/json")])
    return data.encode("ascii")
