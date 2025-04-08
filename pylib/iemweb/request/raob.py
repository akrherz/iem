""".. title:: RAOB Data Service

Return to `API Services </api/#cgi>`_

Documentation for /cgi-bin/request/raob.py
------------------------------------------

Emits RAOB data in CSV format.

Changelog
---------

- 2025-04-08: Migration to pydantic validation.

Example Requests
----------------

Provide the KOAX sounding info for July 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/raob.py?station=KOAX&\
sts=2024-07-01T00:00:00Z&ets=2024-08-01T00:00:00Z

"""

from datetime import datetime, timezone
from io import StringIO

from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    dl: bool = Field(
        False,
        description="Download CSV instead of displaying it",
    )
    sts: datetime = Field(..., description="Start time in UTC")
    ets: datetime = Field(..., description="End time in UTC")
    station: str = Field(
        "KOAX", description="IEM Station Identifier", max_length=4
    )


def m(val):
    """Helper"""
    if val is None:
        return "M"
    return val


@with_sqlalchemy_conn("raob")
def fetcher(station, sts, ets, conn: Connection = None):
    """Do fetching"""
    sio = StringIO()
    stations = [station]
    if station.startswith("_"):
        nt = NetworkTable("RAOB", only_online=False)
        stations = nt.sts[station]["name"].split("--")[1].strip().split(",")

    res = conn.execute(
        sql_helper("""
    SELECT f.valid at time zone 'UTC', p.levelcode, p.pressure, p.height,
    p.tmpc, p.dwpc, p.drct, round((p.smps * 1.94384)::numeric,0),
    p.bearing, p.range_miles, f.station from
    raob_profile p JOIN raob_flights f on
    (f.fid = p.fid) WHERE f.station = ANY(:stations)
    and valid >= :sts and valid < :ets
    """),
        {"stations": stations, "sts": sts, "ets": ets},
    )
    sio.write(
        "station,validUTC,levelcode,pressure_mb,height_m,tmpc,"
        "dwpc,drct,speed_kts,bearing,range_sm\n"
    )
    for row in res:
        sio.write(
            ("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n")
            % (
                row[10],
                m(row[0]),
                m(row[1]),
                m(row[2]),
                m(row[3]),
                m(row[4]),
                m(row[5]),
                m(row[6]),
                m(row[7]),
                m(row[8]),
                m(row[9]),
            )
        )
    return sio.getvalue().encode("ascii", "ignore")


def friendly_date(form, key):
    """More forgiving date conversion"""
    val = form.get(key)
    try:
        val = val.strip()
        if len(val.split()) == 1:
            dt = datetime.strptime(val, "%m/%d/%Y")
        else:
            dt = datetime.strptime(val, "%m/%d/%Y %H:%M")
        dt = dt.replace(tzinfo=timezone.utc)
    except Exception:
        return (
            f"Invalid {key} date provided, should be '%m/%d/%Y %H:%M'"
            " in UTC timezone"
        )
    return dt


@iemapp(help=__doc__, schema=Schema, default_tz="UTC")
def application(environ, start_response):
    """Go Main Go"""
    station = environ["station"]
    sts = environ["sts"]
    ets = environ["ets"]
    if environ["dl"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            (
                "Content-Disposition",
                "attachment; "
                f"filename={station}_{sts:%Y%m%d%H}_{ets:%Y%m%d%H}.txt",
            ),
        ]
    else:
        headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    return [fetcher(station, sts, ets)]
