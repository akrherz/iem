""".. title:: JSON Webcam Data

Return to `JSON Services </json/>`_

Changelog
---------

- 2024-08-05: Initial documtation update

"""

import datetime
import json
from zoneinfo import ZoneInfo

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    cid: str = Field(default="ISUC-006", description="Camera ID")
    date: str = Field(default=None, description="Date in YYYYMMDD format")
    end_ts: str = Field(
        default="202101012359", description="End Timestamp in UTC"
    )
    start_ts: str = Field(
        default="202101010000", description="Start Timestamp in UTC"
    )


def dance(cid, start_ts, end_ts):
    """Go get the dictionary of data we need and deserve"""
    data = {"images": []}
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            text("""
        SELECT valid at time zone 'UTC', drct from camera_log where
        cam = :cid and valid >= :sts and valid < :ets
    """),
            {"cid": cid, "sts": start_ts, "ets": end_ts},
        )
        for row in res:
            uri = row[0].strftime(
                "https://mesonet.agron.iastate.edu/archive/"
                f"data/%Y/%m/%d/camera/{cid}/{cid}_%Y%m%d%H%M.jpg"
            )
            data["images"].append(
                {
                    "valid": row[0].strftime("%Y-%m-%dT%H:%M:00Z"),
                    "drct": row[1],
                    "href": uri,
                }
            )
    return data


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    cid = environ["cid"]
    start_ts = environ["start_ts"]
    end_ts = environ["end_ts"]
    date = environ["date"]
    if date is not None:
        start_ts = datetime.datetime.strptime(date, "%Y%m%d")
        start_ts = start_ts.replace(tzinfo=ZoneInfo("America/Chicago"))
        end_ts = start_ts + datetime.timedelta(days=1)
    else:
        if start_ts is None:
            raise IncompleteWebRequest("GET start_ts= parameter missing")
        start_ts = datetime.datetime.strptime(start_ts, "%Y%m%d%H%M")
        start_ts = start_ts.replace(tzinfo=ZoneInfo("UTC"))
        end_ts = datetime.datetime.strptime(end_ts, "%Y%m%d%H%M")
        end_ts = end_ts.replace(tzinfo=ZoneInfo("UTC"))

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(dance(cid, start_ts, end_ts)).encode("ascii")]
