""".. title:: Return UGCs for a given state.

Return to `JSON Services </json/>`.

Documentation for /json/state_ugc.json
--------------------------------------

This service returns a simple listing of NWS UGC codes associated with the
given state code.  Presently, this only returns those codes that are presently
valid.

Changelog
---------

- 2024-08-12: Initial documentation update

Example Requests
----------------

Return any zone codes associated with Lake Michigan (LM).

https://mesonet.agron.iastate.edu/json/state_ugc.py?state=LM

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    state: str = Field(
        default="IA",
        description="state indentifier",
        pattern="^[A-Z]{2}$",
    )


@iemapp(
    memcachekey=lambda e: f"/json/state_ugc|{e['state']}",
    content_type="application/json",
    help=__doc__,
    schema=Schema,
    memcacheexpire=0,
)
def application(environ, start_response):
    """Answer request."""
    data = {
        "ugcs": [],
    }
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(
                """
            SELECT ugc, name from ugcs WHERE substr(ugc,1,2) = :state and
            ugc is not null and end_ts is null and name is not null
            ORDER by name ASC
        """
            ),
            {
                "state": environ["state"],
            },
        )
        for row in res.mappings():
            data["ugcs"].append(
                {
                    "ugc": row["ugc"],
                    "name": row["name"],
                }
            )
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(data)
