""".. title:: Pilot Weather Report (PIREP) Data Service

Return to `API Services </api/#cgi>`_

Documentation for /cgi-bin/request/gis/pireps.py
------------------------------------------------

This service emits processed and raw PIREP data.  At this time, you must
request 120 days or less of data at one time if you do not filter the request.

Changelog
---------

- 2025-01-09: Added `FL` field (Flight Level) to the output, units are `ft`.
- 2024-06-28: Initital documentation release
- 2024-07-31: A `product_id` field was added to the output, but only non-null
  for PIREPs after about 18 UTC on 31 July 2024.  Someday, a backfill may
  happen.

Example Requests
----------------

Provide all PIREPs for 31 July 2024 UTC over Minneapolis ARTCC:

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/pireps.py?\
sts=2024-07-31T00:00:00Z&ets=2024-08-01T00:00:00Z&artcc=ZMP&fmt=csv

Same request, but return a shapefile:

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/pireps.py?\
sts=2024-07-31T00:00:00Z&ets=2024-08-01T00:00:00Z&artcc=ZMP&fmt=shp

"""

import zipfile
from datetime import timedelta
from io import BytesIO, StringIO
from typing import Annotated

import shapefile
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

from iemweb.fields import LATITUDE_FIELD, LONGITUDE_FIELD


class Schema(CGIModel):
    """See how we are called."""

    artcc: ListOrCSVType = Field(
        default_factory=list,
        description="The ARTCC to limit the query to, use _ALL for all",
    )
    ets: Annotated[
        AwareDatetime | None, Field(description="The end time of the query")
    ] = None
    fmt: Annotated[str, Field(description="The format of the output file")] = (
        "shp"
    )
    sts: Annotated[
        AwareDatetime | None, Field(description="The start time of the query")
    ] = None
    year1: Annotated[
        int | None,
        Field(
            description="The start year of the query, when sts not provided",
        ),
    ] = None
    month1: Annotated[
        int | None,
        Field(
            description="The start month of the query, when sts not provided",
        ),
    ] = None
    day1: Annotated[
        int | None,
        Field(
            description="The start day of the query, when sts is not provided",
        ),
    ] = None
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
    lat: LATITUDE_FIELD = 41.99
    lon: LONGITUDE_FIELD = -91.99
    hour1: int = Field(
        default=0,
        description="The start hour of the query, when sts is not provided",
    )
    minute1: int = Field(
        default=0,
        description="The start minute of the query, when sts is not provided",
    )
    year2: Annotated[
        int | None,
        Field(
            description="The end year of the query, when ets is not provided",
        ),
    ] = None
    month2: Annotated[
        int | None,
        Field(
            description="The end month of the query, when ets is not provided",
        ),
    ] = None
    day2: Annotated[
        int | None,
        Field(
            description="The end day of the query, when ets is not provided",
        ),
    ] = None
    hour2: int = Field(
        default=0,
        description="The end hour of the query, when ets is not provided",
    )
    minute2: int = Field(
        default=0,
        description="The end minute of the query, when ets is not provided",
    )


def run(query: Schema, start_response: callable):
    """Go run!"""
    artcc_sql = ""
    if "_ALL" not in query.artcc and query.artcc:
        artcc_sql = " artcc = ANY(:artcc) and "
    params = {
        "artcc": query.artcc,
        "distance": query.degrees,
        "lat": query.lat,
        "lon": query.lon,
        "sts": query.sts,
        "ets": query.ets,
    }

    spatialsql = ""
    if query.filter:
        spatialsql = (
            "ST_Distance(geom::geometry, ST_Point(:lon, :lat, 4326) "
            ") <= :distance and "
        )
    else:
        if (query.ets - query.sts).days > 120:
            query.ets = query.sts + timedelta(days=120)
    sql = """
        SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
        case when is_urgent then 'T' else 'F' end,
        substr(replace(aircraft_type, ',', ' '), 0, 40),
        substr(replace(report, ',', ' '), 0, 255),
        substr(trim(substring(replace(report, ',', ' '),
            '/IC([^/]*)/?')), 0, 255) as icing,
        substr(trim(substring(replace(report, ',', ' '),
            '/TB([^/]*)/?')), 0, 255) as turb,
        artcc, product_id, flight_level,
        ST_y(geom::geometry) as lat, ST_x(geom::geometry) as lon
        from pireps WHERE {spatialsql} {artcc_sql}
        valid >= :sts and valid < :ets ORDER by valid ASC
        """
    fn = f"pireps_{query.sts:%Y%m%d%H%M}_{query.ets:%Y%m%d%H%M}"

    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper(sql, spatialsql=spatialsql, artcc_sql=artcc_sql), params
        )
        if res.rowcount == 0:
            start_response("200 OK", [("Content-type", "text/plain")])
            return b"ERROR: no results found for your query"

        if query.fmt == "csv":
            sio = StringIO()
            headers = [
                ("Content-type", "application/octet-stream"),
                ("Content-Disposition", f"attachment; filename={fn}.csv"),
            ]
            start_response("200 OK", headers)
            sio.write(
                "VALID,URGENT,AIRCRAFT,REPORT,ICING,TURBULENCE,ATRCC,"
                "PRODUCT_ID,FL,LAT,LON\n"
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
            shp.field("FL", "N", 6, 0)
            shp.field("LAT", "F", 7, 4)
            shp.field("LON", "F", 9, 4)
            for row in res:
                # Can't support null geoms like other formats do.
                if row[-1] is not None:
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
def application(environ: dict, start_response: callable):
    """Do something fun!"""
    query: Schema = environ["_cgimodel_schema"]
    if query.sts is None or query.ets is None:
        raise IncompleteWebRequest("GET start/end time parameters missing.")
    return [run(query, start_response)]
