""".. title:: Daily CLImate Reports

Return to `API Services </api/#json>`_ |
View `Map Frontend </nws/climap.php>`_
or `Table Frontend </nws/clitable.php>`_

Documentation for /geojson/cli.py
---------------------------------

This service emits atomic data for a given date of NWS CLImate reporting.  This
is based on a parsing of the `CLI` product, which contains daily climate
summaries for mostly airport weather stations.  This service primarily is used
to output GeoJSON, but there is a CSV option as well.

Changelog
---------

- 2024-08-09: Initial documentation update

Example Usage
-------------

Provide CLI data for 2024-07-01 in GeoJSON format:

https://mesonet.agron.iastate.edu/geojson/cli.py?dt=2024-07-01&fmt=geojson

Same data, but in CSV format:

https://mesonet.agron.iastate.edu/geojson/cli.py?dt=2024-07-01&fmt=csv

Same data, but in CSV format and force download:

https://mesonet.agron.iastate.edu/geojson/cli.py?dt=2024-07-01&fmt=csv&dl=1

"""

from datetime import date

import simplejson as json
from pydantic import Field
from pyiem.reference import TRACE_VALUE
from pyiem.webutil import CGIModel, iemapp
from simplejson import encoder

encoder.FLOAT_REPR = lambda o: format(o, ".2f")


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None, description="JSONP callback function name."
    )
    dl: bool = Field(default=False, description="Force download of CSV file.")
    dt: date = Field(default=date.today(), description="Date of interest.")
    fmt: str = Field(
        default="geojson",
        description="The output format requested.",
        pattern="^(geojson|csv)$",
    )


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


def get_data(cursor, ts, fmt):
    """Get the data for this timestamp"""
    data = {"type": "FeatureCollection", "features": []}
    # Fetch the daily values
    cursor.execute(
        """
    select station, name, product, state, wfo, valid,
    round(st_x(geom)::numeric, 4)::float as lon,
    round(st_y(geom)::numeric, 4)::float as lat,
    high, high_normal, high_record, high_record_years, high_time,
    low, low_normal, low_record, low_record_years, low_time,
    precip, precip_normal, precip_month, precip_jan1, precip_jan1_normal,
    precip_jul1, precip_dec1, precip_dec1_normal, precip_record,
    precip_record_years, snow_normal,
    precip_month_normal, snow, snow_month, snow_jun1, snow_jul1,
    snow_dec1, snow_record, snow_jul1_normal,
    snow_dec1_normal, snow_month_normal, snow_record_years,
    precip_jun1, precip_jun1_normal,
    round(((case when snow_jul1 < 0.1 then 0 else snow_jul1 end)
        - snow_jul1_normal)::numeric, 2) as snow_jul1_depart,
    round(((case when precip_jan1 < 0.1 then 0 else precip_jan1 end)
        - precip_jan1_normal)::numeric, 2) as precip_jan1_depart,
    average_sky_cover,
    resultant_wind_speed, resultant_wind_direction,
    highest_wind_speed, highest_wind_direction,
    highest_gust_speed, highest_gust_direction,
    average_wind_speed, snowdepth
    from cli_data c JOIN stations s on (c.station = s.id)
    WHERE s.network = 'NWSCLI' and c.valid = %s
    """,
        (ts,),
    )
    for i, row in enumerate(cursor):
        data["features"].append(
            {
                "type": "Feature",
                "id": i,
                "properties": {
                    "station": row["station"],
                    "state": row["state"],
                    "lon": row["lon"],
                    "lat": row["lat"],
                    "valid": row["valid"].strftime("%Y-%m-%d"),
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
                    "precip_month_normal": f2_sanitize(
                        row["precip_month_normal"]
                    ),
                    "precip_jan1": f2_sanitize(row["precip_jan1"]),
                    "precip_jan1_normal": f2_sanitize(
                        row["precip_jan1_normal"]
                    ),
                    "precip_jan1_depart": f2_sanitize(
                        row["precip_jan1_depart"]
                    ),
                    "precip_jun1": f2_sanitize(row["precip_jun1"]),
                    "precip_jun1_normal": f2_sanitize(
                        row["precip_jun1_normal"]
                    ),
                    "precip_jul1": f2_sanitize(row["precip_jul1"]),
                    "precip_dec1": f2_sanitize(row["precip_dec1"]),
                    "precip_dec1_normal": f2_sanitize(
                        row["precip_dec1_normal"]
                    ),
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
                    "highest_wind_speed": int_sanitize(
                        row["highest_wind_speed"]
                    ),
                    "highest_wind_direction": int_sanitize(
                        row["highest_wind_direction"]
                    ),
                    "highest_gust_speed": int_sanitize(
                        row["highest_gust_speed"]
                    ),
                    "highest_gust_direction": int_sanitize(
                        row["highest_gust_direction"]
                    ),
                    "average_wind_speed": f1_sanitize(
                        row["average_wind_speed"]
                    ),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["lon"], row["lat"]],
                },
            }
        )
    if fmt == "geojson":
        return json.dumps(data)
    cols = (
        "station,lon,lat,valid,name,state,wfo,high,high_record,"
        "high_record_years,"
        "high_normal,high_time,low,low_record,low_record_years,low_normal,"
        "low_time,precip,precip_normal,precip_month,precip_jan1,"
        "precip_jan1_normal,precip_jul1,precip_dec1,precip_dec1_normal,"
        "precip_record,precip_record_years,precip_jan1_depart,"
        "snow,snowdepth,snow_normal,snow_month,snow_jun1,snow_jul1,snow_dec1,"
        "snow_record,snow_record_years,snow_jul1_normal,snow_dec1_normal,"
        "snow_month_normal,snow_jul1_depart,average_sky_cover"
    )
    res = cols + "\n"
    for feat in data["features"]:
        for col in cols.split(","):
            val = feat["properties"][col]
            if isinstance(val, (list, tuple)):
                res += f"{' '.join([str(s) for s in val])},"
            else:
                res += f"{val},"
        res += "\n"
    return res


def get_ct(environ):
    """Get the content-type."""
    fmt = environ["fmt"]
    if fmt == "geojson":
        return "application/vnd.geo+json"
    if fmt == "csv" and environ["dl"]:
        return "application/octet-stream"
    if fmt == "csv":
        return "text/plain"
    return "text/plain"


def get_mckey(environ):
    """Figure out the memcache key."""
    return f"/geojson/cli/{environ['dt']:%Y%m%d}?fmt={environ['fmt']}"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type=get_ct,
    memcachekey=get_mckey,
    memcacheexpire=300,
    iemdb="iem",
    iemdb_cursorname="cursor",
)
def application(environ, start_response):
    """see how we are called"""
    fmt = environ["fmt"]

    headers = []
    if fmt == "geojson":
        headers.append(("Content-type", "application/vnd.geo+json"))
    elif fmt == "csv" and environ["dl"]:
        headers.extend(
            [
                ("Content-type", "application/octet-stream"),
                (
                    "Content-disposition",
                    f"attachment; filename=cli{environ['dt']:%Y%m%d}.csv",
                ),
            ]
        )
    else:
        headers.append(("Content-type", "text/plain"))

    data = get_data(environ["iemdb.iem.cursor"], environ["dt"], fmt)
    start_response("200 OK", headers)
    return data.encode("ascii")
