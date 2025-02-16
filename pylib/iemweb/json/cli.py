""".. title:: NWS Daily CLImate Data

Return to `API Services </api/#json>`_

Documentation for /json/cli.py
------------------------------

This service returns atomic daily climate data found in the NWS CLI text
products.

Changelog
---------

- 2025-01-30: Corrected bug in station validation
- 2024-08-14: Documentation update

Example Requests
----------------

Get all daily climate data for Des Moines, IA during 2024

https://mesonet.agron.iastate.edu/json/cli.py?station=KDSM&year=2024

"""

from datetime import date

import simplejson as json
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.reference import TRACE_VALUE
from pyiem.webutil import CGIModel, iemapp
from simplejson import encoder

encoder.FLOAT_REPR = lambda o: format(o, ".2f")


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    fmt: str = Field(
        default="json",
        description="The format of the output, either json or csv",
    )
    station: str = Field(
        default="KDSM",
        description="The station identifier to query for",
        max_length=4,
        pattern="^[A-Z0-9]{4}$",
    )
    year: int = Field(default=2019, description="The year to query for")


def departure(ob, climo):
    """Compute a departure value"""
    if ob is None or climo is None:
        return "M"
    return ob - climo


def int_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return int(val)


def f1_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return round(val, 1)


def f2_sanitize(val):
    """convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return round(val, 2)


def get_data(conn, station, year, fmt):
    """Get the data for this timestamp"""
    data = {"results": []}
    # Fetch the daily values
    res = conn.execute(
        sql_helper("""
        select station, name, product, state, wfo, valid,
        round(st_x(geom)::numeric, 4)::float as st_x,
        round(st_y(geom)::numeric, 4)::float as st_y,
        high, high_normal, high_record, high_record_years, high_time,
        low, low_normal, low_record, low_record_years, low_time,
        precip, precip_month, precip_jan1, precip_jan1_normal,
        precip_jul1, precip_dec1, precip_dec1_normal, precip_record,
        precip_record_years, precip_normal, snow_normal,
        precip_month_normal, snow, snow_month, snow_jun1, snow_jul1,
        snow_dec1, snow_record, snow_jul1_normal, snow_record_years,
        snow_dec1_normal, snow_month_normal, precip_jun1, precip_jun1_normal,
        round(((case when snow_jul1 < 0.1 then 0 else snow_jul1 end)
            - snow_jul1_normal)::numeric, 2) as snow_jul1_depart,
        average_sky_cover,
        resultant_wind_speed, resultant_wind_direction,
        highest_wind_speed, highest_wind_direction,
        highest_gust_speed, highest_gust_direction,
        average_wind_speed, snowdepth
        from cli_data c JOIN stations s on (c.station = s.id)
        WHERE s.network = 'NWSCLI' and c.station = :station
        and c.valid >= :sts and c.valid <= :ets
        ORDER by c.valid ASC
    """),
        {
            "station": station,
            "sts": date(year, 1, 1),
            "ets": date(year, 12, 31),
        },
    )
    for row in res.mappings():
        data["results"].append(
            {
                "station": row["station"],
                "valid": row["valid"].strftime("%Y-%m-%d"),
                "state": row["state"],
                "wfo": row["wfo"],
                "link": f"/api/1/nwstext/{row['product']}",
                "product": row["product"],
                "name": row["name"],
                "high": int_sanitize(row["high"]),
                "high_record": int_sanitize(row["high_record"]),
                "high_record_years": row["high_record_years"],
                "high_normal": int_sanitize(row["high_normal"]),
                "high_depart": departure(row["high"], row["high_normal"]),
                "high_time": row["high_time"],
                "low": int_sanitize(row["low"]),
                "low_record": int_sanitize(row["low_record"]),
                "low_record_years": row["low_record_years"],
                "low_normal": int_sanitize(row["low_normal"]),
                "low_depart": departure(row["low"], row["low_normal"]),
                "low_time": row["low_time"],
                "precip": f2_sanitize(row["precip"]),
                "precip_normal": f2_sanitize(row["precip_normal"]),
                "precip_month": f2_sanitize(row["precip_month"]),
                "precip_month_normal": f2_sanitize(row["precip_month_normal"]),
                "precip_jan1": f2_sanitize(row["precip_jan1"]),
                "precip_jan1_normal": f2_sanitize(row["precip_jan1_normal"]),
                "precip_jun1": f2_sanitize(row["precip_jun1"]),
                "precip_jun1_normal": f2_sanitize(row["precip_jun1_normal"]),
                "precip_jul1": f2_sanitize(row["precip_jul1"]),
                "precip_dec1": f2_sanitize(row["precip_dec1"]),
                "precip_dec1_normal": f2_sanitize(row["precip_dec1_normal"]),
                "precip_record": f2_sanitize(row["precip_record"]),
                "precip_record_years": row["precip_record_years"],
                "snow": f1_sanitize(row["snow"]),
                "snowdepth": f1_sanitize(row["snowdepth"]),
                "snow_normal": f1_sanitize(row["snow_normal"]),
                "snow_month": f1_sanitize(row["snow_month"]),
                "snow_jun1": f1_sanitize(row["snow_jun1"]),
                "snow_jul1": f1_sanitize(row["snow_jul1"]),
                "snow_dec1": f1_sanitize(row["snow_dec1"]),
                "snow_record": f1_sanitize(row["snow_record"]),
                "snow_record_years": row["snow_record_years"],
                "snow_jul1_normal": f1_sanitize(row["snow_jul1_normal"]),
                "snow_jul1_depart": f1_sanitize(row["snow_jul1_depart"]),
                "snow_dec1_normal": f1_sanitize(row["snow_dec1_normal"]),
                "snow_month_normal": f1_sanitize(row["snow_month_normal"]),
                "average_sky_cover": f1_sanitize(row["average_sky_cover"]),
                "resultant_wind_speed": f1_sanitize(
                    row["resultant_wind_speed"]
                ),
                "resultant_wind_direction": int_sanitize(
                    row["resultant_wind_direction"]
                ),
                "highest_wind_speed": int_sanitize(row["highest_wind_speed"]),
                "highest_wind_direction": int_sanitize(
                    row["highest_wind_direction"]
                ),
                "highest_gust_speed": int_sanitize(row["highest_gust_speed"]),
                "highest_gust_direction": int_sanitize(
                    row["highest_gust_direction"]
                ),
                "average_wind_speed": f1_sanitize(row["average_wind_speed"]),
            }
        )
    if fmt == "json":
        return json.dumps(data)
    cols = (
        "station,valid,name,state,wfo,high,high_record,high_record_years,"
        "high_normal,high_time,low,low_record,low_record_years,low_normal,"
        "low_time,precip,precip_normal,precip_month,precip_jan1,"
        "precip_jan1_normal,precip_jul1,precip_dec1,precip_dec1_normal,"
        "precip_record,precip_record_years,"
        "snow,snowdepth,snow_normal,snow_month,snow_jun1,snow_jul1,snow_dec1,"
        "snow_record,snow_record_years,snow_jul1_normal,snow_dec1_normal,"
        "snow_month_normal,snow_jul1_depart,average_sky_cover"
    )
    res = cols + "\n"
    for feat in data["results"]:
        for col in cols.split(","):
            val = feat[col]
            if isinstance(val, (list, tuple)):
                res += f"{' '.join([str(s) for s in val])},"
            else:
                res += f"{val},"
        res += "\n"
    return res


def get_mckey(environ: dict):
    """Get the memcache key."""
    return f"/json/cli/{environ['station']}/{environ['year']}/{environ['fmt']}"


def get_ct(environ: dict) -> str:
    """Get the content type."""
    if environ["fmt"] == "json":
        return "application/json"
    return "text/plain"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type=get_ct,
    memcachekey=get_mckey,
    memcacheexpire=300,
)
def application(environ, start_response):
    """Answer request."""
    station = environ["station"]
    year = environ["year"]
    fmt = environ["fmt"]

    with get_sqlalchemy_conn("iem") as conn:
        data = get_data(conn, station, year, fmt)
    start_response("200 OK", [("Content-type", get_ct(environ))])
    return data.encode("ascii")
