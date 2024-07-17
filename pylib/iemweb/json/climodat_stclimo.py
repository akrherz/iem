"""Dump daily computed climatology direct from the database"""

import datetime
import json

from pydantic import Field
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, title="JSONP Callback")
    eyear: int = Field(datetime.datetime.now().year + 1, title="End Year")
    station: str = Field("IA0200", title="Station Identifier", max_length=6)
    syear: int = Field(1800, title="Start Year")


def run(cursor, station, syear, eyear):
    """Do something"""
    cursor.execute(
        """
    WITH data as (
      SELECT sday, year, precip,
      avg(precip) OVER (PARTITION by sday) as avg_precip,
      high, rank() OVER (PARTITION by sday ORDER by high DESC nulls last)
        as max_high,
      avg(high) OVER (PARTITION by sday) as avg_high,
      rank() OVER (PARTITION by sday ORDER by high ASC nulls last)
        as min_high,
      low, rank() OVER (PARTITION by sday ORDER by low DESC nulls last)
        as max_low,
      avg(low) OVER (PARTITION by sday) as avg_low,
      rank() OVER (PARTITION by sday ORDER by low ASC nulls last)
        as min_low,
      rank() OVER (PARTITION by sday ORDER by precip DESC nulls last)
        as max_precip,
      max(high - low) OVER (PARTITION by sday) as max_range,
      min(high - low) OVER (PARTITION by sday) as min_range
      from alldata WHERE station = %s and year >= %s and year < %s),

    max_highs as (
      SELECT sday, high, array_agg(year) as years from data
      where max_high = 1 GROUP by sday, high),
    min_highs as (
      SELECT sday, high, array_agg(year) as years from data
      where min_high = 1 GROUP by sday, high),

    max_lows as (
      SELECT sday, low, array_agg(year) as years from data
      where max_low = 1 GROUP by sday, low),
    min_lows as (
      SELECT sday, low, array_agg(year) as years from data
      where min_low = 1 GROUP by sday, low),

    max_precip as (
      SELECT sday, precip, array_agg(year) as years from data
      where max_precip = 1 GROUP by sday, precip),

    avgs as (
      SELECT sday, count(*) as cnt, max(avg_precip) as p,
      max(max_range) as max_range, min(min_range) as min_range,
      max(avg_high) as h, max(avg_low) as l from data GROUP by sday)

    SELECT a.sday, a.cnt,
    a.h, xh.high as xh_high, xh.years as xh_years,
    nh.high as nh_high, nh.years as nh_years,
    a.l, xl.low as xl_low, xl.years as xl_years,
    nl.low as nl_low, nl.years as nl_years,
    a.p, mp.precip, mp.years as mp_years, a.max_range, a.min_range
    from avgs a, max_highs xh, min_highs nh, max_lows xl, min_lows nl,
    max_precip mp
    WHERE xh.sday = a.sday and xh.sday = nh.sday and xh.sday = xl.sday and
    xh.sday = nl.sday and xh.sday = mp.sday ORDER by sday ASC
    """,
        (station, syear, eyear),
    )
    res = {
        "station": station,
        "start_year": syear,
        "end_year": eyear,
        "climatology": [],
    }
    for row in cursor:
        res["climatology"].append(
            dict(
                month=int(row["sday"][:2]),
                day=int(row["sday"][2:]),
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
                max_range=row["max_range"],
                min_range=row["min_range"],
            )
        )
    return json.dumps(res)


def get_key(environ):
    """Figure out the cache key"""
    return (
        f"/json/climodat_stclimo/{environ['station']}/"
        f"{environ['syear']}/{environ['eyear']}"
    )


@iemapp(
    iemdb="coop",
    iemdb_cursorname="cursor",
    help=__doc__,
    schema=Schema,
    memcachekey=get_key,
)
def application(environ, start_response):
    """Answer request."""
    station = environ["station"]
    syear = environ["syear"]
    eyear = environ["eyear"]

    res = run(environ["iemdb.coop.cursor"], station, syear, eyear)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
