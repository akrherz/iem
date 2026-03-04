""".. title:: JSON Webcam Data

Return to `API Services </api/>`_

Changelog
---------

- 2024-08-05: Initial documtation update

"""

import json
from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, iemapp

from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    cid: Annotated[str, Field(description="Camera ID")] = "ISUC-006"
    date: Annotated[
        str | None, Field(description="Date in YYYYMMDD format")
    ] = None
    end_ts: Annotated[str, Field(description="End Timestamp in UTC")] = (
        "202101012359"
    )
    start_ts: Annotated[str, Field(description="Start Timestamp in UTC")] = (
        "202101010000"
    )


def dance(cid, start_ts, end_ts):
    """Go get the dictionary of data we need and deserve"""
    data = json_response_dict({"images": []})
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            sql_helper("""
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
    dt = environ["date"]
    if dt is not None:
        start_ts = datetime.strptime(dt, "%Y%m%d")
        start_ts = start_ts.replace(tzinfo=ZoneInfo("America/Chicago"))
        end_ts = start_ts + timedelta(days=1)
    else:
        if start_ts is None:
            raise IncompleteWebRequest("GET start_ts= parameter missing")
        start_ts = datetime.strptime(start_ts, "%Y%m%d%H%M")
        start_ts = start_ts.replace(tzinfo=ZoneInfo("UTC"))
        end_ts = datetime.strptime(end_ts, "%Y%m%d%H%M")
        end_ts = end_ts.replace(tzinfo=ZoneInfo("UTC"))

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(dance(cid, start_ts, end_ts)).encode("ascii")]
