""".. title:: Service for NEXRAD Attributes GeoJSON

Return to `API Services </json/#json>`_.

Documentation for /geojson/nexrad_attr.py
-----------------------------------------

This service emits GeoJSON of NEXRAD attributes.  If no `valid` parameter is
provided, it provides the most recent storm attributes per NEXRAD that are
valid within the past 30 minutes.  If a `valid` parameter is provided, it will
search for the nearest in time volume scan and provide attributes for that
time.

Changelog
---------

- 2024-07-03: Initial documentation release.

Example Usage
-------------

Return the most recent NEXRAD attributes in GeoJSON format:

https://mesonet.agron.iastate.edu/geojson/nexrad_attr.py

Return attributes around the time of 05:10UTC on 10 August 2024:

https://mesonet.agron.iastate.edu/geojson/nexrad_attr.py?\
valid=2024-08-10T05:10:00Z

Same request, but return CSV

https://mesonet.agron.iastate.edu/geojson/nexrad_attr.py?\
valid=2024-08-10T05:10:00Z&fmt=csv

"""

import datetime
import json
from zoneinfo import ZoneInfo

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(
        default=None, description="Optional JSONP callback function name"
    )
    fmt: str = Field(
        default="geojson",
        description="The format of the output, geojson or csv",
        pattern="^(geojson|csv)$",
    )
    valid: datetime.datetime = Field(
        default=None, description="The timestamp to request data for, in UTC."
    )


def run(conn, valid, fmt):
    """Actually do the hard work of getting the geojson"""

    if valid is None:
        res = conn.execute(
            text("""
            SELECT ST_x(geom) as lon, ST_y(geom) as lat, *,
            valid at time zone 'UTC' as utc_valid from
            nexrad_attributes WHERE valid > now() - '30 minutes'::interval
            """)
        )
    else:
        valid = valid.replace(tzinfo=ZoneInfo("UTC"))
        tbl = f"nexrad_attributes_{valid:%Y}"
        res = conn.execute(
            text(f"""
    with vcps as (
        SELECT distinct nexrad, valid from {tbl}
        where valid between :sts and :ets),
    agg as (
        select nexrad, valid,
        row_number() OVER (PARTITION by nexrad
            ORDER by (greatest(valid, :valid) - least(valid, :valid)) ASC)
        as rank from vcps)
    SELECT n.*, ST_x(geom) as lon, ST_y(geom) as lat,
    n.valid at time zone 'UTC' as utc_valid
    from {tbl} n, agg a WHERE
    a.rank = 1 and a.nexrad = n.nexrad and a.valid = n.valid
    ORDER by n.nexrad ASC
    """),
            {
                "sts": valid - datetime.timedelta(minutes=10),
                "ets": valid + datetime.timedelta(minutes=10),
                "valid": valid,
            },
        )

    if fmt == "geojson":
        data = {
            "type": "FeatureCollection",
            "features": [],
            "generation_time": utc().strftime(ISO8601),
            "count": res.rowcount,
        }
        for i, row in enumerate(res):
            row = row._asdict()
            data["features"].append(
                {
                    "type": "Feature",
                    "id": i,
                    "properties": {
                        "nexrad": row["nexrad"],
                        "storm_id": row["storm_id"],
                        "azimuth": row["azimuth"],
                        "range": row["range"],
                        "tvs": row["tvs"],
                        "meso": row["meso"],
                        "posh": row["posh"],
                        "poh": row["poh"],
                        "max_size": row["max_size"],
                        "vil": row["vil"],
                        "max_dbz": row["max_dbz"],
                        "max_dbz_height": row["max_dbz_height"],
                        "top": row["top"],
                        "drct": row["drct"],
                        "sknt": row["sknt"],
                        "valid": row["utc_valid"].strftime(ISO8601),
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row["lon"], row["lat"]],
                    },
                }
            )
        return json.dumps(data)
    data = (
        "nexrad,storm_id,azimuth,range,tvs,meso,posh,poh,max_size,"
        "vil,max_dbz,max_dbz_height,top,drct,sknt,valid\n"
    )
    for row in res:
        row = row._asdict()
        data += ",".join(
            [
                str(x)
                for x in [
                    row["nexrad"],
                    row["storm_id"],
                    row["azimuth"],
                    row["range"],
                    row["tvs"],
                    row["meso"],
                    row["posh"],
                    row["poh"],
                    row["max_size"],
                    row["vil"],
                    row["max_dbz"],
                    row["max_dbz_height"],
                    row["top"],
                    row["drct"],
                    row["sknt"],
                    row["utc_valid"].strftime(ISO8601),
                ]
            ]
        )
        data += "\n"
    return data


def get_ct(environ):
    """Figure out the content type."""
    fmt = environ["fmt"]
    if fmt == "geojson":
        return "application/vnd.geo+json"
    return "text/csv"


def get_mckey(environ):
    """Figure out our memcache key."""
    valid = environ["valid"]
    if valid is None:
        valid = utc()
    return f"/geojson/nexrad_attr.{environ['fmt']}|{valid:%Y%m%d%H%M%S}"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type=get_ct,
    memcachekey=get_mckey,
    memcacheexpire=60,
)
def application(environ, start_response):
    """Do Something"""
    fmt = environ["fmt"]
    headers = [("Content-type", get_ct(environ))]

    with get_sqlalchemy_conn("radar") as conn:
        res = run(conn, environ["valid"], fmt)
    start_response("200 OK", headers)
    return res.encode("ascii")
