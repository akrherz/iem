""".. title:: Generate Climodat Day Climatology GeoJSON

Return to `API Services </api/#json>`_ or
`Climodat Frontend </COOP/extremes.php>`_.

Documentation for /geojson/climodat_dayclimo.py
-----------------------------------------------

This service returns a GeoJSON representation of the daily climatology
for a given day of the year.  The data is derived from the IEM's
`climodat` database table.

Usage Examples
~~~~~~~~~~~~~~

Provide Iowa's daily climatology for January 1st:

https://mesonet.agron.iastate.edu/geojson/climodat_dayclimo.py\
?network=IACLIMATE&month=1&day=1

"""

import datetime
import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import Connection, text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(default=None, title="JSONP Callback")
    day: int = Field(default=1, ge=1, le=31)
    month: int = Field(default=1, ge=1, le=12)
    syear: int = Field(default=1800, ge=1800, le=2050)
    eyear: int = Field(
        default=datetime.datetime.now().year + 1, ge=1800, le=2050
    )
    network: str = Field(
        default="IACLIMATE",
        title="Network Identifier",
        pattern="^[A-Z][A-Z][A-Z_0-9]{2,30}$",
    )


def run(conn: Connection, network, month, day, syear, eyear):
    """Do something"""

    nt = NetworkTable(network)
    sday = f"{month:02.0f}{day:02.0f}"
    table = f"alldata_{network[:2]}"
    res = conn.execute(
        text(f"""
    WITH data as (
      SELECT station, year, precip,
      avg(precip) OVER (PARTITION by station) as avg_precip,
      high, rank() OVER (PARTITION by station ORDER by high DESC nulls last)
        as max_high,
      avg(high) OVER (PARTITION by station) as avg_high,
      rank() OVER (PARTITION by station ORDER by high ASC nulls last)
        as min_high,
      low, rank() OVER (PARTITION by station ORDER by low DESC nulls last)
        as max_low,
      avg(low) OVER (PARTITION by station) as avg_low,
      rank() OVER (PARTITION by station ORDER by low ASC nulls last)
        as min_low,
      rank() OVER (PARTITION by station ORDER by precip DESC nulls last)
        as max_precip
      from {table} WHERE sday = :sday and year >= :syear and year < :eyear),

    max_highs as (
      SELECT station, high, array_agg(year) as years from data
      where max_high = 1 GROUP by station, high),
    min_highs as (
      SELECT station, high, array_agg(year) as years from data
      where min_high = 1 GROUP by station, high),

    max_lows as (
      SELECT station, low, array_agg(year) as years from data
      where max_low = 1 GROUP by station, low),
    min_lows as (
      SELECT station, low, array_agg(year) as years from data
      where min_low = 1 GROUP by station, low),

    max_precip as (
      SELECT station, precip, array_agg(year) as years from data
      where max_precip = 1 GROUP by station, precip),

    avgs as (
      SELECT station, count(*) as cnt, max(avg_precip) as p,
      max(avg_high) as h, max(avg_low) as l from data GROUP by station)

    SELECT a.station, a.cnt, a.h, xh.high as xh_high, xh.years as xh_years,
    nh.high as nh_high, nh.years as nh_years, a.l, xl.low as xl_low,
    xl.years as xl_years,
    nl.low as nl_low, nl.years as nl_years, a.p, mp.precip,
    mp.years as mp_years
    from avgs a, max_highs xh, min_highs nh, max_lows xl, min_lows nl,
    max_precip mp
    WHERE xh.station = a.station and xh.station = nh.station
    and xh.station = xl.station and
    xh.station = nl.station and xh.station = mp.station and
    xh.high is not null and a.l is not null ORDER by station ASC

    """),
        {"sday": sday, "syear": syear, "eyear": eyear},
    )
    data = {
        "type": "FeatureCollection",
        "month": month,
        "day": day,
        "network": network,
        "features": [],
    }

    for i, row in enumerate(res.mappings()):
        if row["station"] not in nt.sts:
            continue
        props = dict(
            station=row["station"],
            years=row["cnt"],
            avg_high=float(row["h"]),
            max_high=row["xh_high"],
            max_high_years=row["xh_years"],
            min_high=row["nh_high"],
            min_high_years=row["nh_years"],
            avg_low=float(row["l"]),
            max_low=row["xl_low"],
            max_low_years=row["xl_years"],
            min_low=row["nl_low"],
            min_low_years=row["nl_years"],
            avg_precip=float(row["p"]),
            max_precip=row["precip"],
            max_precip_years=row["mp_years"],
        )
        data["features"].append(
            {
                "type": "Feature",
                "id": i,
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        nt.sts[row["station"]]["lon"],
                        nt.sts[row["station"]]["lat"],
                    ],
                },
            }
        )

    return json.dumps(data)


def get_mckey(environ: dict) -> str:
    """Get the memcache key"""
    return (
        f"/geojson/climodat_dayclimo/{environ['network']}/{environ['month']}/"
        f"{environ['day']}/{environ['syear']}/{environ['eyear']}"
    )


@iemapp(
    help=__doc__, memcacheexpire=7200, memcachekey=get_mckey, schema=Schema
)
def application(environ, start_response):
    """Main()"""
    headers = [("Content-type", "application/json")]

    network = environ["network"]
    month = environ["month"]
    day = environ["day"]
    syear = environ["syear"]
    eyear = environ["eyear"]
    with get_sqlalchemy_conn("coop") as conn:
        res = run(conn, network, month, day, syear, eyear)

    start_response("200 OK", headers)
    return res.encode("ascii")
