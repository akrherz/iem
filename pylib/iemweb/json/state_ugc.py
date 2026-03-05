""".. title:: Return UGCs for a given state.

Return to `API Services </api/#json>`.

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

from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import CALLBACK_FIELD, STATE_FIELD
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    state: STATE_FIELD = "IA"


@iemapp(
    memcachekey=lambda e: f"/json/state_ugc|{e['state']}",
    content_type="application/json",
    help=__doc__,
    schema=Schema,
    memcacheexpire=0,
)
def application(environ, start_response):
    """Answer request."""
    data = json_response_dict(
        {
            "ugcs": [],
        }
    )
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper(
                """
            SELECT distinct ugc, name from ugcs WHERE substr(ugc,1,2) = :state
            and ugc is not null and end_ts is null and name is not null
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
