"""Dump daily computed climatology direct from the database"""
import datetime
import json

from pymemcache.client import Client
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def run(station, syear, eyear):
    """Do something"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()

    table = f"alldata_{station[:2]}"
    cursor.execute(
        f"""
    WITH data as (
      SELECT sday, year, precip,
      avg(precip) OVER (PARTITION by sday) as avg_precip,
      high, rank() OVER (PARTITION by sday ORDER by high DESC) as max_high,
      avg(high) OVER (PARTITION by sday) as avg_high,
      rank() OVER (PARTITION by sday ORDER by high ASC) as min_high,
      low, rank() OVER (PARTITION by sday ORDER by low DESC) as max_low,
      avg(low) OVER (PARTITION by sday) as avg_low,
      rank() OVER (PARTITION by sday ORDER by low ASC) as min_low,
      rank() OVER (PARTITION by sday ORDER by precip DESC) as max_precip,
      max(high - low) OVER (PARTITION by sday) as max_range,
      min(high - low) OVER (PARTITION by sday) as min_range
      from {table} WHERE station = %s and year >= %s and year < %s),

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

    SELECT a.sday, a.cnt, a.h, xh.high, xh.years,
    nh.high, nh.years, a.l, xl.low, xl.years,
    nl.low, nl.years, a.p, mp.precip, mp.years, a.max_range, a.min_range
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
                month=int(row[0][:2]),
                day=int(row[0][2:]),
                years=row[1],
                avg_high=float(row[2]),
                max_high=row[3],
                max_high_years=row[4],
                min_high=row[5],
                min_high_years=row[6],
                avg_low=float(row[7]),
                max_low=row[8],
                max_low_years=row[9],
                min_low=row[10],
                min_low_years=row[11],
                avg_precip=float(row[12]),
                max_precip=row[13],
                max_precip_years=row[14],
                max_range=row[15],
                min_range=row[16],
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    station = fields.get("station", "IA0200").upper()
    syear = int(fields.get("syear", 1800))
    eyear = int(fields.get("eyear", datetime.datetime.now().year + 1))
    cb = fields.get("callback", None)

    mckey = f"/json/climodat_stclimo/{station}/{syear}/{eyear}"
    mc = Client("iem-memcached.local:11211")
    res = mc.get(mckey)
    if not res:
        res = run(station, syear, eyear)
        mc.set(mckey, res, 86400)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
