""".. title:: Pilot Weather Report (PIREP) Data Service

Documentation for /cgi-bin/request/gis/pireps.py
------------------------------------------------

This service emits processed and raw PIREP data.  At this time, you must
request 120 days or less of data at one time if you do not filter the request.

Changelog
---------

- 2024-06-28: Initital documentation release
- 2024-07-31: A `product_id` field was added to the output, but only non-null
for PIREPs after about 18 UTC on 31 July 2024.  Someday, a backfill may happen.

Example Requests
----------------

Provide all PIREPs for the month of June 2024 over Chicago ARTCC in CSV:

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/pireps.py?\
sts=2024-06-01T00:00:00Z&ets=2024-07-01T00:00:00Z&artcc=ZAU&fmt=csv

"""

import datetime
import zipfile
from io import BytesIO, StringIO

import shapefile
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    artcc: ListOrCSVType = Field(
        default=[],
        description="The ARTCC to limit the query to, use _ALL for all",
    )
    ets: AwareDatetime = Field(
        default=None, description="The end time of the query"
    )
    fmt: str = Field(
        default="shp", description="The format of the output file"
    )
    sts: AwareDatetime = Field(
        default=None, description="The start time of the query"
    )
    year1: int = Field(
        default=2000,
        description="The start year of the query, when sts is not provided",
    )
    month1: int = Field(
        default=1,
        description="The start month of the query, when sts is not provided",
    )
    day1: int = Field(
        default=1,
        description="The start day of the query, when sts is not provided",
    )
    degrees: float = Field(
        default=1.0,
        description="The distance in degrees for a spatial filter",
        gt=0,
        lt=90,
    )
    filter: bool = Field(
        default=False,
        description="Should we filter by distance from a point?",
    )
    lat: float = Field(
        default=41.99,
        description="The latitude of the point to filter by",
    )
    lon: float = Field(
        default=-91.99,
        description="The longitude of the point to filter by",
    )
    hour1: int = Field(
        default=0,
        description="The start hour of the query, when sts is not provided",
    )
    minute1: int = Field(
        default=0,
        description="The start minute of the query, when sts is not provided",
    )
    year2: int = Field(
        default=2000,
        description="The end year of the query, when ets is not provided",
    )
    month2: int = Field(
        default=1,
        description="The end month of the query, when ets is not provided",
    )
    day2: int = Field(
        default=1,
        description="The end day of the query, when ets is not provided",
    )
    hour2: int = Field(
        default=0,
        description="The end hour of the query, when ets is not provided",
    )
    minute2: int = Field(
        default=0,
        description="The end minute of the query, when ets is not provided",
    )


def run(environ, start_response):
    """Go run!"""
    artcc_sql = ""
    if "_ALL" not in environ["artcc"] and environ["artcc"]:
        artcc_sql = " artcc = ANY(:artcc) and "
    params = {
        "artcc": environ["artcc"],
        "distance": environ["degrees"],
        "lat": environ["lat"],
        "lon": environ["lon"],
        "sts": environ["sts"],
        "ets": environ["ets"],
    }

    spatialsql = ""
    if environ["filter"]:
        spatialsql = (
            "ST_Distance(geom::geometry, ST_SetSRID(ST_Point(:lon, :lat), "
            "4326)) <= :distance and "
        )
    else:
        if (environ["ets"] - environ["sts"]).days > 120:
            environ["ets"] = environ["sts"] + datetime.timedelta(days=120)
    sql = f"""
        SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
        case when is_urgent then 'T' else 'F' end,
        substr(replace(aircraft_type, ',', ' '), 0, 40),
        substr(replace(report, ',', ' '), 0, 255),
        substr(trim(substring(replace(report, ',', ' '),
            '/IC([^/]*)/?')), 0, 255) as icing,
        substr(trim(substring(replace(report, ',', ' '),
            '/TB([^/]*)/?')), 0, 255) as turb,
        artcc, product_id,
        ST_y(geom::geometry) as lat, ST_x(geom::geometry) as lon
        from pireps WHERE {spatialsql} {artcc_sql}
        valid >= :sts and valid < :ets ORDER by valid ASC
        """
    fn = f"pireps_{environ['sts']:%Y%m%d%H%M}_{environ['ets']:%Y%m%d%H%M}"

    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(text(sql), params)
        if res.rowcount == 0:
            start_response("200 OK", [("Content-type", "text/plain")])
            return b"ERROR: no results found for your query"

        if environ["fmt"] == "csv":
            sio = StringIO()
            headers = [
                ("Content-type", "application/octet-stream"),
                ("Content-Disposition", f"attachment; filename={fn}.csv"),
            ]
            start_response("200 OK", headers)
            sio.write(
                "VALID,URGENT,AIRCRAFT,REPORT,ICING,TURBULENCE,ATRCC,LAT,LON,"
                "PRODUCT_ID\n"
            )
            for row in res:
                sio.write(",".join([str(s) for s in row]) + "\n")
            return sio.getvalue().encode("ascii", "ignore")

        shpio = BytesIO()
        shxio = BytesIO()
        dbfio = BytesIO()

        with shapefile.Writer(shx=shxio, dbf=dbfio, shp=shpio) as shp:
            shp.field("VALID", "C", 12)
            shp.field("URGENT", "C", 1)
            shp.field("AIRCRAFT", "C", 40)
            shp.field("REPORT", "C", 255)  # Max field size is 255
            shp.field("ICING", "C", 255)  # Max field size is 255
            shp.field("TURB", "C", 255)  # Max field size is 255
            shp.field("ARTCC", "C", 3)
            shp.field("PROD_ID", "C", 36)
            shp.field("LAT", "F", 7, 4)
            shp.field("LON", "F", 9, 4)
            for row in res:
                if row[-1] is None:
                    continue
                shp.point(row[-1], row[-2])
                shp.record(*row)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="ascii") as fh:
            zf.writestr(f"{fn}.prj", fh.read())
        zf.writestr(f"{fn}.shp", shpio.getvalue())
        zf.writestr(f"{fn}.shx", shxio.getvalue())
        zf.writestr(f"{fn}.dbf", dbfio.getvalue())
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)
    return zio.getvalue()


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do something fun!"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("GET start time parameters missing.")
    return [run(environ, start_response)]
