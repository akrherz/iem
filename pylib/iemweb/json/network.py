""".. title:: Legacy Network Metadata Service

Return to `API Services </api/#json>`_

Changelog
---------

- 2024-07-26: Initial documentation release

Example Requests
----------------

Return metadata for the SCAN network:

https://mesonet.agron.iastate.edu/json/network.py?network=SCAN

"""

import json
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="JSONP callback function name")
    ] = None
    network: Annotated[
        str,
        Field(
            description="Optional network identifier to filter results by",
        ),
    ] = "IA_ASOS"


def get_mckey(environ):
    """Return the memcache key for this request."""
    return f"json_network_{environ['network']}"


@iemapp(
    memcachekey=get_mckey,
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
            sql_helper(
                """
            select id, name, ST_x(geom) as lon, ST_y(geom) as lat
            from stations where network = :network order by id asc
        """
            ),
            {
                "network": environ["network"],
            },
        )
        for row in res.mappings():
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
