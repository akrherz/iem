""".. title:: Audit of NWS CLI Data

Return to `API Services </api/#json>`_ or the
`User Frontend </nws/cli-audit/>_`

Documentation for /json/cli_audit.py
------------------------------------

This app intends to show how the sausage gets made for daily high and low
temperature reports from the major ASOS sites.

Changelog
---------

- 2026-02-26: Updates to hopefully have full closure over potential changes
  found with subsequent CLI and CF6 updates.  Previously, a 144 hour forward
  time window was assumed.
- 2026-02-25: Initial implementation

Example Requests
----------------

Audit CLI for Des Moines on 25 Feb 2026

https://mesonet.agron.iastate.edu/json/cli_audit.py\
?station=KDSM&date=2026-02-25

"""

from datetime import date as dateobj
from datetime import datetime, timedelta
from math import isfinite
from typing import Annotated
from zoneinfo import ZoneInfo

import simplejson as json
from pydantic import BaseModel, Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.nws.products.cf6 import parser as cf6_parser
from pyiem.nws.products.cli import parser as cli_parser
from pyiem.nws.products.dsm import parser as dsm_parser
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from simplejson import encoder
from sqlalchemy.engine import Connection

from iemweb import error_log
from iemweb.util import get_ct, json_response_dict

encoder.FLOAT_REPR = lambda o: format(o, ".2f")


class Event(BaseModel):
    """Events that our logic generates and later materialized to response."""

    varname: Annotated[str, Field(description="The variable name")]
    source: Annotated[str, Field(description="Source of Event")]
    value: Annotated[
        float,
        Field(
            description="The value of the event",
            allow_inf_nan=False,
        ),
    ]
    utc_valid: Annotated[
        datetime, Field(description="The UTC valid time of the event")
    ]
    local_valid: Annotated[
        datetime, Field(description="The local valid time of the event")
    ]
    description: Annotated[
        str, Field(description="A human readable description of the event")
    ]
    link: Annotated[str, Field("Web Resource")]


class Schema(CGIModel):
    """See how we are called."""

    station: Annotated[
        str,
        Field(
            description="The 4 character station identifier to query for",
            max_length=4,
            pattern="^[A-Z0-9]{4}$",
        ),
    ] = "KDSM"
    date: Annotated[dateobj, Field(description="The date of interest")]


def as_finite_float(value) -> float | None:
    """Convert value into finite float, return None when unavailable."""
    if value in (None, "M"):
        return None
    try:
        fvalue = float(value)
    except (TypeError, ValueError):
        return None
    return fvalue if isfinite(fvalue) else None


@with_sqlalchemy_conn("iem")
def find_last_product(
    station: str,
    dt: dateobj,
    table: str,
    conn: Connection | None = None,
) -> str | None:
    """Figure out the last product ID for the given type."""
    res = conn.execute(
        sql_helper(
            """
        select product from {table} where valid = :valid and station = :station
                                  """,
            table=table,
        ),
        {"valid": dt, "station": station},
    )
    if res.rowcount == 0:
        return None
    return res.fetchone()[0]


@with_sqlalchemy_conn("asos")
def add_metar_events(
    events: list[Event],
    station: str,
    dt: dateobj,
    tzinfo: ZoneInfo,
    conn: Connection | None = None,
):
    """Compute events and add to the events list."""
    dbstation = (
        station.removeprefix("K") if station.startswith("K") else station
    )
    # This is tricky. We need a period from 11:50 PM Standard (no DST)
    # Till midnight standard the next day
    midnight_local = datetime(dt.year, dt.month, dt.day, tzinfo=tzinfo)
    if midnight_local.dst() != timedelta(0):
        # We are in DST, so we need to shift back an hour
        midnight_local = midnight_local - timedelta(hours=1)
    sts = midnight_local - timedelta(minutes=10)
    # Jump well into the next day and then set back to midnight
    ets = (midnight_local + timedelta(hours=26)).replace(hour=0, minute=0)
    res = conn.execute(
        sql_helper("""
        select valid at time zone 'UTC' as utc_valid, tmpf, max_tmpf_6hr,
        min_tmpf_6hr, metar from alldata where
        station = :station and valid >= :sts and valid < :ets and
        report_type in (3, 4) order by valid asc
                                  """),
        {
            "station": dbstation,
            "sts": sts,
            "ets": ets,
        },
    )
    running_high = -999
    running_low = 999
    for row in res.mappings():
        tmpf = as_finite_float(row["tmpf"])
        max_tmpf_6hr = as_finite_float(row["max_tmpf_6hr"])
        min_tmpf_6hr = as_finite_float(row["min_tmpf_6hr"])
        utc_valid = row["utc_valid"].replace(tzinfo=ZoneInfo("UTC"))
        local_valid = utc_valid.astimezone(tzinfo)
        offset = local_valid - sts
        if (
            max_tmpf_6hr is not None
            and offset > timedelta(hours=3)
            and max_tmpf_6hr > running_high
        ):
            events.append(
                Event(
                    source="METAR max 6hr",
                    varname="high",
                    value=max_tmpf_6hr,
                    utc_valid=utc_valid,
                    local_valid=local_valid,
                    description=f"{row['metar']}",
                    link="",
                )
            )
            running_high = max_tmpf_6hr
        if (
            min_tmpf_6hr is not None
            and offset > timedelta(hours=3)
            and min_tmpf_6hr < running_low
        ):
            events.append(
                Event(
                    varname="low",
                    source="METAR min 6hr",
                    value=min_tmpf_6hr,
                    utc_valid=utc_valid,
                    local_valid=local_valid,
                    description=f"{row['metar']}",
                    link="",
                )
            )
            running_low = min_tmpf_6hr
        if tmpf is not None:
            if tmpf > running_high:
                events.append(
                    Event(
                        varname="high",
                        source="METAR",
                        value=tmpf,
                        utc_valid=utc_valid,
                        local_valid=local_valid,
                        description=row["metar"],
                        link="",
                    )
                )
                running_high = tmpf
            if tmpf < running_low:
                events.append(
                    Event(
                        varname="low",
                        source="METAR",
                        value=tmpf,
                        utc_valid=utc_valid,
                        local_valid=local_valid,
                        description=row["metar"],
                        link="",
                    )
                )
                running_low = tmpf


@with_sqlalchemy_conn("mesosite")
def get_timezone(station: str, conn: Connection | None = None):
    """Figure out something simple."""
    dbstation = (
        station.removeprefix("K") if station.startswith("K") else station
    )

    res = conn.execute(
        sql_helper("""
        SELECT tzname from stations where id = :station and network ~* 'ASOS'
                                  """),
        {"station": dbstation},
    )
    row = res.fetchone()
    if row is None:
        return "America/Chicago"
    return row[0]


@with_sqlalchemy_conn("afos")
def add_dsm_events(
    events: list[Event],
    environ: dict,
    station: str,
    dt: dateobj,
    tzinfo: ZoneInfo,
    conn: Connection | None = None,
):
    """We now process DSMs"""
    sts = utc(dt.year, dt.month, dt.day)
    ets = sts + timedelta(hours=48)  # meh?
    res = conn.execute(
        sql_helper("""
        select entered at time zone 'UTC' as utc_entered, data, wmo, source,
        pil
        from products where
        entered > :sts and entered < :ets and pil = :pil
        order by entered asc
                                  """),
        {
            "sts": sts,
            "ets": ets,
            "pil": f"DSM{station[1:]}",
        },
    )
    for row in res.mappings():
        # Ugly, we need to convert this into a full noaaport product
        text = f"""000
{row["wmo"]} {row["source"]} {row["utc_entered"]:%d%H%M}
{row["pil"]}
{row["data"]}
"""
        try:
            utc_valid = row["utc_entered"].replace(tzinfo=ZoneInfo("UTC"))
            local_valid = utc_valid.astimezone(tzinfo)
            dsm = dsm_parser(
                text,
                utcnow=utc_valid,
                ugc_provider={},
            )
            for dsmprod in dsm.data:
                if dsmprod.date != dt or dsmprod.station != station:
                    continue
                high = dsmprod.groupdict.get("high")
                low = dsmprod.groupdict.get("low")
                high_value = as_finite_float(high)
                low_value = as_finite_float(low)
                clean_text = (
                    row["data"]
                    .encode("ascii", errors="ignore")
                    .decode("ascii")
                )
                if high_value is not None:
                    events.append(
                        Event(
                            varname="high",
                            source="DSM",
                            value=high_value,
                            utc_valid=utc_valid,
                            local_valid=local_valid,
                            description=clean_text,
                            link=(
                                "https://mesonet.agron.iastate.edu/"
                                f"p.php?pid={dsm.get_product_id()}"
                            ),
                        )
                    )
                if low_value is not None:
                    events.append(
                        Event(
                            varname="low",
                            source="DSM",
                            value=low_value,
                            utc_valid=utc_valid,
                            local_valid=local_valid,
                            description=clean_text,
                            link=(
                                "https://mesonet.agron.iastate.edu/"
                                f"p.php?pid={dsm.get_product_id()}"
                            ),
                        )
                    )

        except Exception as exp:
            error_log(environ, exp)
            continue


@with_sqlalchemy_conn("afos")
def add_cli_events(
    events: list[Event],
    environ: dict,
    station: str,
    dt: dateobj,
    tzinfo: ZoneInfo,
    conn: Connection | None = None,
):
    """We now process CLI events"""
    last_cli = find_last_product(station, dt, "cli_data")
    if last_cli is None:
        return
    sts = utc(dt.year, dt.month, dt.day)
    ets = datetime.strptime(last_cli[:12], "%Y%m%d%H%M").replace(
        tzinfo=ZoneInfo("UTC")
    ) + timedelta(minutes=1)
    res = conn.execute(
        sql_helper("""
        select entered at time zone 'UTC' as utc_entered, data
        from products where
        entered > :sts and entered < :ets and pil = :pil
        order by entered asc
                                  """),
        {
            "sts": sts,
            "ets": ets,
            "pil": f"CLI{station[1:]}",
        },
    )
    for row in res.mappings():
        try:
            cli = cli_parser(
                row["data"],
                utcnow=row["utc_entered"].replace(tzinfo=ZoneInfo("UTC")),
                ugc_provider={},
            )
            for entry in cli.data:
                if entry["cli_valid"] != dt or entry["db_station"] != station:
                    continue
                high = entry["data"].get("temperature_maximum")
                high_time = entry["data"].get("temperature_maximum_time")
                low = entry["data"].get("temperature_minimum")
                low_time = entry["data"].get("temperature_minimum_time")
                high_value = as_finite_float(high)
                low_value = as_finite_float(low)
                if high_value is not None:
                    events.append(
                        Event(
                            varname="high",
                            source="CLI",
                            value=high_value,
                            utc_valid=cli.valid,
                            local_valid=cli.valid.astimezone(tzinfo),
                            description=f"{high} at {high_time}",
                            link=(
                                "https://mesonet.agron.iastate.edu/"
                                f"p.php?pid={cli.get_product_id()}"
                            ),
                        )
                    )
                if low_value is not None:
                    events.append(
                        Event(
                            varname="low",
                            source="CLI",
                            value=low_value,
                            utc_valid=cli.valid,
                            local_valid=cli.valid.astimezone(tzinfo),
                            description=f"{low} at {low_time}",
                            link=(
                                "https://mesonet.agron.iastate.edu/"
                                f"p.php?pid={cli.get_product_id()}"
                            ),
                        )
                    )

        except Exception as exp:
            error_log(environ, exp)
            continue


@with_sqlalchemy_conn("afos")
def add_cf6_events(
    events: list[Event],
    environ: dict,
    station: str,
    dt: dateobj,
    tzinfo: ZoneInfo,
    conn: Connection | None = None,
):
    """We now process CLI events"""
    last_cf6 = find_last_product(station, dt, "cf6_data")
    if last_cf6 is None:
        return
    sts = utc(dt.year, dt.month, dt.day)
    ets = datetime.strptime(last_cf6[:12], "%Y%m%d%H%M").replace(
        tzinfo=ZoneInfo("UTC")
    ) + timedelta(minutes=1)
    res = conn.execute(
        sql_helper("""
        select entered at time zone 'UTC' as utc_entered, data
        from products where
        entered > :sts and entered < :ets and pil = :pil
        order by entered asc
                                  """),
        {
            "sts": sts,
            "ets": ets,
            "pil": f"CF6{station[1:]}",
        },
    )
    for row in res.mappings():
        try:
            cf6 = cf6_parser(
                row["data"],
                utcnow=row["utc_entered"].replace(tzinfo=ZoneInfo("UTC")),
                ugc_provider={},
            )
            for valid, entry in cf6.df.iterrows():
                if valid != dt or cf6.station != station:
                    continue
                high = entry.get("max")
                low = entry.get("min")
                high_value = as_finite_float(high)
                low_value = as_finite_float(low)
                if high_value is not None:
                    events.append(
                        Event(
                            varname="high",
                            source="CF6",
                            value=high_value,
                            utc_valid=cf6.valid,
                            local_valid=cf6.valid.astimezone(tzinfo),
                            description=f"{high}",
                            link=(
                                "https://mesonet.agron.iastate.edu/"
                                f"p.php?pid={cf6.get_product_id()}"
                            ),
                        )
                    )
                if low_value is not None:
                    events.append(
                        Event(
                            varname="low",
                            source="CF6",
                            value=low_value,
                            utc_valid=cf6.valid,
                            local_valid=cf6.valid.astimezone(tzinfo),
                            description=f"{low}",
                            link=(
                                "https://mesonet.agron.iastate.edu/"
                                f"p.php?pid={cf6.get_product_id()}"
                            ),
                        )
                    )

        except Exception as exp:
            error_log(environ, exp)
            continue


def get_mckey(environ: dict):
    """Get the memcache key."""
    return f"/json/cli_audit/{environ['station']}/{environ['date']}"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type=get_ct,
    memcachekey=get_mckey,
    memcacheexpire=300,
)
def application(environ: dict, start_response: callable):
    """Answer request."""
    station = environ["station"]
    dt = environ["date"]
    # Create a dataframe to store events that we calculate, which then gets
    # sorted and placed into the response objects
    events: list[Event] = []
    tzname = get_timezone(station)
    tzinfo = ZoneInfo(tzname)
    add_metar_events(events, station, dt, tzinfo)
    add_dsm_events(events, environ, station, dt, tzinfo)
    add_cli_events(events, environ, station, dt, tzinfo)
    add_cf6_events(events, environ, station, dt, tzinfo)

    high_events = [e for e in events if e.varname == "high"]
    low_events = [e for e in events if e.varname == "low"]
    high_events.sort(key=lambda x: x.utc_valid)
    low_events.sort(key=lambda x: x.utc_valid)

    response = json_response_dict(
        {
            "station": station,
            "date": f"{dt:%Y-%m-%d}",
            "tzname": tzname,
            "high": {
                "events": [e.model_dump(mode="json") for e in high_events],
            },
            "low": {
                "events": [e.model_dump(mode="json") for e in low_events],
            },
        }
    )

    headers = [("Content-type", get_ct(environ))]
    start_response("200 OK", headers)
    return json.dumps(response).encode("utf-8")
