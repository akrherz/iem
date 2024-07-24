""".. title:: Sounding/RAOB JSON Service

Return to `JSON Services </json/>`_

Documentation for /json/raob.py
-------------------------------

This service emits a JSON representating of sounding data.  You can approach
this service either with a sounding station and timestamp or just a timestamp.

Changelog
---------

- 2024-07-24: Initial documentation

Example Usage
-------------

Provide the Omaha sounding for 2024-07-24 00:00 UTC:

https://mesonet.agron.iastate.edu/json/raob.py?\
station=KOAX&ts=2024-07-24T00:00:00Z

Provide all soundings for the morning of 2024-03-24 12Z, but only include 500
hPa data:

https://mesonet.agron.iastate.edu/json/raob.py?\
ts=2024-03-24T12:00:00Z&pressure=500

"""

import datetime
import json

import numpy as np
import pandas as pd
from pydantic import Field, field_validator
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

json.encoder.FLOAT_REPR = lambda o: format(o, ".2f")


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP Callback")
    pressure: int = Field(-1, description="Pressure Level of Interest")
    station: str = Field(
        default=None,
        description="3(assuming K***) or 4 char Station Identifier",
        min_length=3,
        max_length=4,
    )
    ts: datetime.datetime = Field(
        ...,
        description="Timestamp of Interest, ISO-8601 preferred",
    )

    @field_validator("ts", mode="before")
    @classmethod
    def rectify_ts(cls, value):
        """Ensure we have a valid timestamp."""
        if value.find("T") > 0:
            # Assume ISO
            dt = datetime.datetime.strptime(value[:16], "%Y-%m-%dT%H:%M")
        else:
            dt = datetime.datetime.strptime(value[:12], "%Y%m%d%H%M")

        return dt.replace(tzinfo=datetime.timezone.utc)

    @field_validator("station", mode="before")
    @classmethod
    def rectify_station(cls, value):
        """Ensure we have a valid station identifier."""
        if len(value) == 3:
            return f"K{value}"
        return value


def safe(val):
    """Be careful"""
    if val is None or np.isnan(val):
        return None
    return float(val)


def run(ts, sid, pressure):
    """Actually do some work!"""
    res = {"profiles": []}
    if ts.year > datetime.datetime.utcnow().year or ts.year < 1946:
        return json.dumps(res)

    stationlimiter = ""
    params = {"valid": ts, "pid": pressure}
    if sid is not None:
        stationlimiter = " f.station = :sid and "
        params["sid"] = sid
        if sid.startswith("_"):
            # Magic here
            nt = NetworkTable("RAOB", only_online=False)
            ids = (
                nt.sts.get(sid, {})
                .get("name", f" -- {sid}")
                .split("--")[1]
                .strip()
                .split()
            )
            if len(ids) > 1:
                stationlimiter = " f.station = ANY(:sid) and "
                params["sid"] = ids
    pressurelimiter = ""
    if pressure > 0:
        pressurelimiter = " and p.pressure = :pid "
    with get_sqlalchemy_conn("raob") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT f.station, p.pressure, p.height,
            round(p.tmpc::numeric,1) as tmpc,
            round(p.dwpc::numeric,1) as dwpc, p.drct,
            round((p.smps * 1.94384)::numeric,0) as sknt
            from raob_profile_{ts:%Y} p JOIN raob_flights f
                on (p.fid = f.fid)
            WHERE {stationlimiter} f.valid = :valid {pressurelimiter}
            ORDER by f.station, p.pressure DESC
            """
            ),
            conn,
            params=params,
            index_col=None,
        )
    for station, gdf in df.groupby("station"):
        profile = []
        for _, row in gdf.iterrows():
            profile.append(
                dict(
                    pres=safe(row["pressure"]),
                    hght=safe(row["height"]),
                    tmpc=safe(row["tmpc"]),
                    dwpc=safe(row["dwpc"]),
                    drct=safe(row["drct"]),
                    sknt=safe(row["sknt"]),
                )
            )
        res["profiles"].append(
            dict(
                station=station,
                valid=ts.strftime(ISO8601),
                profile=profile,
            )
        )
    return json.dumps(res)


def get_mckey(environ: dict) -> str:
    """Figure out the key."""
    return (
        f"/json/raob/{environ['ts']:%Y%m%d%H%M}/{environ['station']}/"
        f"{environ['pressure']}"
    )


@iemapp(memcachekey=get_mckey, memcacheexpire=600, help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    data = run(environ["ts"], environ["station"], environ["pressure"])

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return data.encode("ascii")
