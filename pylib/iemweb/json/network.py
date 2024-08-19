""".. title:: Legacy Network Metadata Service

Return to `API Services </api/#json>`_

Changelog
---------

- 2024-07-26: Initial documentation release

Example Requests
----------------

Return metadata for the IA_ASOS network:

https://mesonet.agron.iastate.edu/json/network.py?network=IA_ASOS

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    network: str = Field(
        default="IA_ASOS",
        description="Optional network identifier to filter results by",
    )


@iemapp(
    memcachekey="/json/network",
    content_type="application/json",
    help=__doc__,
    schema=Schema,
    memcacheexpire=3600,
)
def application(environ, start_response):
    """Answer request."""
    data = {
        "stations": [],
    }
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            text(
                """
            select id, name, ST_x(geom) as lon, ST_y(geom) as lat
            from stations where network = :network order by id asc
        """
            ),
            {
                "network": environ["network"],
            },
        )
        for row in res:
            row = row._asdict()
            data["stations"].append(
                {
                    "id": row["id"],
                    "combo": f"[{row['id']}] {row['name']}",
                    "name": row["name"],
                    "lon": row["lon"],
                    "lat": row["lat"],
                }
            )
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(data)
