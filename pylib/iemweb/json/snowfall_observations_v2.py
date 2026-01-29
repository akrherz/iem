""".. title:: NWS 6 Hour Snowfall Observations v2 service

Return to `API Services </api/#json>`_

This service intends to replicate a JSON file make available by NWS Chicago.

Changelog
---------

- 2025-11-17: Initial Release

Example Requests
----------------

Return current 48-hour snowfall totals for NWS Davenport

https://mesonet.agron.iastate.edu/json/snowfall_observations_v2.py?wfo=DVN

Same for NWS Miami (in case they ever get snow, hehe.)

https://mesonet.agron.iastate.edu/json/snowfall_observations_v2.py?wfo=MFL

"""

from datetime import timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
from pydantic import Field
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="JSONP Callback Name")
    ] = None
    wfo: Annotated[
        str,
        Field(
            description="The WFO to return data for",
            pattern="^[A-Z]{3}$",
        ),
    ] = "DVN"


def dowork(wfo: str) -> list:
    """Actually do stuff"""
    nt = NetworkTable("WFO")
    if wfo not in nt.sts:
        raise IncompleteWebRequest("Unknown WFO")
    tzinfo = ZoneInfo(nt.sts[wfo]["tzname"])
    rows = []
    time_columns = []  # Track column order

    now = utc()
    for _ in range(49):
        if now.hour % 6 == 0:
            localdt = now.astimezone(tzinfo)
            tidx = f"{localdt:%m/%d: %-I %p}"
            time_columns.append(tidx)  # Track insertion order
            service = (
                "http://mesonet.agron.iastate.edu/"
                f"api/1/nws/snowfall_6hour.json?valid={now:%Y-%m-%dT%H}:00"
                f"&wfo={wfo}"
            )
            try:
                resp = httpx.get(service, timeout=15)
                resp.raise_for_status()
                jdata = resp.json()
            except Exception:
                continue
            rows.extend(
                {
                    "Location": entry["name"],
                    "tidx": tidx,
                    "value": entry["value"],
                }
                for entry in jdata["data"]
            )

        now -= timedelta(hours=1)

    if not rows:
        return "[]"

    obs = pd.DataFrame(rows).pivot(
        index="Location",
        columns="tidx",
        values="value",
    )
    # Reindex columns to preserve chronological order
    obs = obs.reindex(columns=time_columns)
    obs["Total 48 hr Snow"] = obs.sum(axis=1)
    # Cleanup trace values
    obs = obs.replace({0.0001: "T"})
    # Represent all values as a string with at most 1 decimal
    obs = obs.map(lambda x: f"{x:.1f}" if isinstance(x, float) else x)

    return obs.reset_index().to_json(orient="records", date_format="iso")


@iemapp(
    help=__doc__,
    memcachekey=lambda env: f"/snowfall_observations_v2/{env['wfo']}",
    memcacheexpire=300,
    schema=Schema,
)
def application(environ, start_response):
    """Answer request."""
    data = dowork(environ["wfo"])
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return data
