""".. title:: Single station currents

Return to `API Services </api/#json>`_

Documentation for /json/current.py
----------------------------------

This is a legacy service that emits the most recent observation for a given
site and network combination.

Changelog
---------

- 2026-03-03: Please migrate usage of root attribute `server_gentime` to
  `generated_at`.
- 2024-08-01: Documentation update

Example Requests
----------------

Return the latest observation for the Ames Airport

https://mesonet.agron.iastate.edu/json/current.py?station=AMW&network=IA_ASOS

"""

import json
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import Connection

from iemweb.fields import CALLBACK_FIELD
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    network: Annotated[
        str,
        Field(
            description="The network identifier, such as IA_ASOS",
            min_length=2,  # OT
            max_length=32,
            pattern="^[A-Z0-9_]+$",
        ),
    ]
    station: Annotated[
        str,
        Field(
            description="The station identifier, such as AMW",
            min_length=3,
            max_length=64,
            pattern=r"^[A-Z0-9_\-]+$",
        ),
    ]


def run(conn: Connection, network, station):
    """Get last ob!"""
    res = conn.execute(
        sql_helper("""
    WITH mystation as (
             SELECT * from stations where id = :id and network = :net),
    lastob as (select *, m.iemid as miemid,
        valid at time zone 'UTC' as utctime,
        valid at time zone m.tzname as localtime
        from current c JOIN mystation m on (c.iemid = m.iemid)),
    summ as (SELECT *, s.pday as s_pday from summary s JOIN lastob o
    on (s.iemid = o.miemid and s.day = date(o.localtime)))
    select * from summ
    """),
        {"id": station, "net": network},
    )
    if res.rowcount == 0:
        return "{}"
    row = res.mappings().fetchone()
    data = json_response_dict({})
    data["server_gentime"] = utc().strftime(ISO8601)
    data["id"] = station
    data["network"] = network
    ob = data.setdefault("last_ob", {})
    ob["local_valid"] = row["localtime"].strftime("%Y-%m-%d %H:%M")
    ob["utc_valid"] = row["utctime"].strftime(ISO8601)
    ob["airtemp[F]"] = row["tmpf"]
    ob["max_dayairtemp[F]"] = row["max_tmpf"]
    ob["min_dayairtemp[F]"] = row["min_tmpf"]
    ob["dewpointtemp[F]"] = row["dwpf"]
    ob["windspeed[kt]"] = row["sknt"]
    ob["winddirection[deg]"] = row["drct"]
    ob["altimeter[in]"] = row["alti"]
    ob["mslp[mb]"] = row["mslp"]
    ob["skycover[code]"] = [
        row["skyc1"],
        row["skyc2"],
        row["skyc3"],
        row["skyc4"],
    ]
    ob["skylevel[ft]"] = [
        row["skyl1"],
        row["skyl2"],
        row["skyl3"],
        row["skyl4"],
    ]
    ob["visibility[mile]"] = row["vsby"]
    ob["raw"] = row["raw"]
    ob["presentwx"] = [] if row["wxcodes"] is None else row["wxcodes"]
    ob["precip_today[in]"] = row["s_pday"]
    ob["c1tmpf[F]"] = row["c1tmpf"]
    ob["srad_1h[J m-2]"] = row["srad_1h_j"]
    for depth in [4, 8, 16, 20, 32, 40, 64, 128]:
        ob[f"tsoil[{depth}in][F]"] = row[f"tsoil_{depth}in_f"]
    return json.dumps(data)


@iemapp(
    memcachekey=lambda x: f"/json/current/{x['network']}/{x['station']}",
    memcacheexpire=120,
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Answer request."""
    network = environ["network"]
    station = environ["station"]

    with get_sqlalchemy_conn("iem") as conn:
        res = run(conn, network, station)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
