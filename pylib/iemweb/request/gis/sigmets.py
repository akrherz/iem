""".. title:: SIGMET Data Service

Return to `User Frontend </request/gis/awc_sigmets.phtml>`_ or
`IEM API Services </api/#cgi>`_.

Documentation for /cgi-bin/request/gis/sigmets.py
-------------------------------------------------

This service emits SIGMET data for a given time period.

Changelog
---------

- 2025-05-14: The raw SIGMET text was added to the outputs.
- 2024-07-11: Migration to pydantic validation and added CSV,Excel format
  options.

Example Requests
----------------

Provide all SIGMETs for 10 Aug 2024 as a shapefile or a KML file.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/sigmets.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/sigmets.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z&format=kml

"""

import tempfile
import zipfile
from collections.abc import Callable
from io import BytesIO, StringIO
from typing import Annotated

import fiona
import geopandas as gpd
import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import ISO8601
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    YEAR_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, iemapp

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    format: Annotated[
        str,
        Field(
            description="Output format, either shp, kml, csv, or excel",
            pattern="^(shp|kml|csv|excel)$",
        ),
    ] = "shp"
    sts: Annotated[AwareDatetime | None, Field(description="Start Time")] = (
        None
    )
    ets: Annotated[AwareDatetime | None, Field(description="End Time")] = None
    year1: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    year2: YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour2: HOUR_FIELD = 0
    minute2: MINUTE_FIELD = 0


def run(query: Schema, start_response: Callable):
    """Do something!"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(  # type: ignore
            sql_helper("""
                select label  || ' ' || sigmet_type as name, label,
                sigmet_type as type,
                issue at time zone 'UTC' as issue,
                expire at time zone 'UTC' as expire, geom,
                product_id as PROD_ID, narrative as TEXT
                from alldata_sigmets WHERE issue >= :sts and
                issue < :ets ORDER by issue ASC
                 """),
            conn,
            params={
                "sts": query.sts,
                "ets": query.ets,
            },
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    for col in ["issue", "expire"]:
        df[col] = df[col].dt.strftime(ISO8601)
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"sigmets_{query.sts:%Y%m%d%H%M}_{query.ets:%Y%m%d%H%M}"
    if query.format == "kml":
        fp = BytesIO()
        with fiona.Env():
            df.to_file(fp, driver="KML", NameField="NAME", engine="fiona")
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.kml"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue()
    if query.format == "csv":
        fp = StringIO()
        df.drop(columns="geom").to_csv(fp, index=False)
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue().encode("ascii")
    if query.format == "excel":
        fp = BytesIO()
        with pd.ExcelWriter(fp) as writer:
            df.drop(columns="geom").to_excel(writer, index=False)
        headers = [
            ("Content-type", EXL),
            ("Content-Disposition", f"attachment; filename={fn}.xlsx"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue()

    schema = {
        "geometry": "Polygon",
        "properties": {
            "NAME": "str:64",
            "LABEL": "str:16",
            "TYPE": "str:1",
            "ISSUE": "str:20",
            "EXPIRE": "str:20",
            "PROD_ID": "str:36",
            "TEXT": "str:255",
        },
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema, engine="fiona")

        zio = BytesIO()
        with zipfile.ZipFile(
            zio, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            with open(PRJFILE, encoding="utf-8") as fh:
                zf.writestr(f"{fn}.prj", fh.read())
            for suffix in ["shp", "shx", "dbf"]:
                zf.write(f"{tmpdir}/{fn}.{suffix}", f"{fn}.{suffix}")
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)

    return zio.getvalue()


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do something fun!"""
    query: Schema = environ["_cgimodel_schema"]
    if query.sts is None or query.ets is None:
        raise IncompleteWebRequest("GET start or end time parameters missing")
    return [run(query, start_response)]
