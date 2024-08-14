""".. title:: Available Archived Webcams at given time

Return to `API Services </api/#json>`.

Documentation for /json/webcams.json
-------------------------------------

This service provides a listing of available archived webcam images for a
given time.  The first entry is to a crude overview map with the NEXRAD
overlain at the given time.

Changelog
---------

- 2024-08-14: Initial documentation update

Example usage
-------------

Return webcam images value at approximately 2020-08-10 17:00 UTC for the KCRG
network:

https://mesonet.agron.iastate.edu/json/webcams.py\
?network=KCRG&ts=2020-08-10T16:00:00Z

The same request, but for the IDOT network:

https://mesonet.agron.iastate.edu/json/webcams.py\
?network=IDOT&ts=2020-08-10T16:00:00Z

Get current imagery from the MCFC network:

https://mesonet.agron.iastate.edu/json/webcams.py?network=MCFC

"""

import json
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

US_CENTRAL = ZoneInfo("America/Chicago")


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    network: str = Field(
        default="KCRG",
        description="Network identifier to look for webcams for.",
    )
    ts: AwareDatetime = Field(
        default=None,
        description=(
            "Archived timestamp to look for imagery, "
            "not providing implies realtime."
        ),
    )


def query_db(conn, environ):
    """Query the database."""
    network = environ["network"]
    ts = environ["ts"]
    params = {
        "network": network,
        "ts": ts,
    }
    if ts is not None and network != "IDOT":
        sql = (
            "SELECT * from camera_log c, webcams w WHERE valid = :ts and "
            "c.cam = w.id and w.network = :network ORDER by name ASC"
        )
    elif ts is not None:
        # RWIS are not exactly on the 5 minute boundary
        sql = (
            "SELECT * from camera_log c, webcams w WHERE valid BETWEEN "
            ":sts and :ets and c.cam = w.id and w.network = :network "
            "ORDER by name ASC, valid ASC"
        )
        params["sts"] = ts - timedelta(minutes=10)
        params["ets"] = ts + timedelta(minutes=10)
    else:
        sql = (
            "SELECT * from camera_current c, webcams w WHERE "
            "valid > (now() - '30 minutes'::interval) and c.cam = w.id "
            "and w.network = :network ORDER by name ASC"
        )
    return conn.execute(text(sql), params)


@iemapp(
    content_type="application/json",
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Answer request."""
    data = {
        "images": [],
    }
    # Add the overview image, le sigh, it wants US Central Time
    extra = (
        ""
        if environ["ts"] is None
        else f"ts={environ['ts'].astimezone(US_CENTRAL):%Y%m%d%H%M}"
    )
    data["images"].append(
        {
            "cid": f"{environ['network']}-000",
            "name": "NEXRAD Overview",
            "county": "",
            "network": "",
            "state": "",
            "url": (
                "https://mesonet.agron.iastate.edu/current/camrad.php?network="
                f"{environ['network']}&{extra}"
            ),
        }
    )
    used = []
    with get_sqlalchemy_conn("mesosite") as conn:
        res = query_db(conn, environ)
        for row in res:
            row = row._asdict()
            if row["cam"] in used:
                continue
            used.append(row["cam"])
            utcvalid = row["valid"].astimezone(timezone.utc)
            url = (
                "https://mesonet.agron.iastate.edu/archive/data/"
                f"{utcvalid:%Y/%m/%d}/camera/"
                f"{row['cam']}/{row['cam']}_{utcvalid:%Y%m%d%H%M}.jpg"
            )
            data["images"].append(
                {
                    "cid": row["id"],
                    "name": row["name"],
                    "county": row["county"],
                    "network": row["network"],
                    "state": row["state"],
                    "url": url,
                }
            )
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return json.dumps(data)
