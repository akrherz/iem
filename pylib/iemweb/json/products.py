""".. title:: Website Products for IEM Time Machine

Return to `API Services </api/#json>`_

Documentation for /json/products.py
-----------------------------------

This service emits a JSON response that drives the
`IEM Time Machine <https://mesonet.agron.iastate.edu/timemachine/>`_.

Changelog
---------

- 2024-07-24: Initital documentation release.

Example Usage
-------------

Nothing much to see here.

https://mesonet.agron.iastate.edu/json/products.py

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")


def add_webcam(conn, data):
    """Append."""
    res = conn.execute(
        text(
            "SELECT * from webcams WHERE network != 'IDOT' "
            "and sts is not null ORDER by network, name"
        )
    )
    for row in res:
        row = row._asdict()
        tpl = (
            "https://mesonet.agron.iastate.edu/archive/data/%Y/%m/%d/"
            f"camera/{row['id']}/{row['id']}_%Y%m%d%H%i.jpg"
        )
        data["products"].append(
            {
                "id": row["id"],
                "template": tpl,
                "name": row["name"],
                "groupname": f"{row['network']} Webcams",
                "interval": 5,
                "time_offset": 0,
                "avail_lag": 0,
                "sts": row["sts"].strftime("%Y-%m-%d"),
            }
        )


def add_archive_products(conn, data):
    """Append."""
    res = conn.execute(
        text(
            "SELECT * from archive_products WHERE sts is not null "
            "ORDER by groupname, name"
        )
    )
    for row in res:
        row = row._asdict()
        data["products"].append(
            {
                "id": row["id"],
                "template": row["template"],
                "name": row["name"],
                "groupname": row["groupname"],
                "interval": row["interval"],
                "time_offset": row["time_offset"],
                "avail_lag": row["avail_lag"],
                "sts": row["sts"].strftime("%Y-%m-%d"),
            }
        )


@iemapp(
    memcachekey="/json/products",
    content_type="application/json",
    help=__doc__,
    schema=Schema,
    memcacheexpire=3600,
)
def application(_environ, start_response):
    """Answer request."""
    data = {
        "products": [],
    }
    with get_sqlalchemy_conn("mesosite") as conn:
        add_archive_products(conn, data)
        add_webcam(conn, data)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(data)
