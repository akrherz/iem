""".. title:: CWAS Data Service

Return to `user frontend </request/gis/cwas.phtml>`_ or
`API Services </api/#cgi>`_

Documentation for /cgi-bin/request/gis/cwas.py
----------------------------------------------

This service emits Center Weather Advisory (CWA) polygons in either KML or
Shapefile format.

Changelog
---------

- 2024-10-07: Fix issue whereby `sts` or `ets` were not provided.
- 2024-08-10: Initital documentation update and usage of pydantic validation.

Example Requests
----------------

Provide all CWAs for 10 Aug 2024 as a shapefile or a KML file.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/cwas.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/cwas.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z&format=kml

"""

import tempfile
import zipfile
from io import BytesIO
from typing import Annotated

import fiona
import geopandas as gpd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
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


class Schema(CGIModel):
    """See how we are called."""

    sts: Annotated[AwareDatetime | None, Field(description="Start Time")] = (
        None
    )
    ets: Annotated[AwareDatetime | None, Field(description="End Time")] = None
    format: Annotated[
        str, Field(description="Output format, either kml or shp")
    ] = "shp"
    year1: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    year2: YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour2: HOUR_FIELD = 23
    minute2: MINUTE_FIELD = 59


def run(query: Schema, start_response: callable):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:00\"Z\"'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "CENTER": "str:4",
            "ISSUE": "str:20",
            "EXPIRE": "str:20",
            "PROD_ID": "str:36",
            "NARRATIV": "str:256",
            "NUMBER": "int",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            sql_helper(
                """select center,
            to_char(issue {common}) as issue,
            to_char(expire {common}) as expire,
            product_id as prod_id, narrative as narrativ, num as number,
            geom from cwas WHERE issue >= :sts and
            issue < :ets ORDER by issue ASC
                       """,
                common=common,
            ),
            conn,
            params={
                "sts": query.sts,
                "ets": query.ets,
            },
            geom_col="geom",
        )  # type: ignore
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"cwas_{query.sts:%Y%m%d%H%M}_{query.ets:%Y%m%d%H%M}"
    if query.format == "kml":
        fp = BytesIO()
        with fiona.Env():
            df.to_file(fp, driver="KML")
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.kml"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue()

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
def application(environ: dict, start_response: callable):
    """Do something fun!"""
    query: Schema = environ["_cgimodel_schema"]
    if query.sts is None or query.ets is None:
        raise IncompleteWebRequest("GET start time parameters missing")
    return [run(query, start_response)]
