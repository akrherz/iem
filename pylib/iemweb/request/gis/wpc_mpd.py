""".. title:: WPC MPD Shapefile Download

Return to `User Frontend </request/gis/wpc_mpd.phtml>`_ or
`API Services </api/#cgi>`_.

Documentation for /cgi-bin/request/gis/wpc_mpd.py
-------------------------------------------------

This service provides a download of the WPC MPD shapefile data for a given
time period.

Changelog
---------

- 2024-10-27: Documentation update

Example Requests
----------------

Provide a shapefile of WPC MPDs for March 2026

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/wpc_mpd.py?\
sts=2026-03-01T00:00Z&ets=2026-04-01T00:00Z

"""

import tempfile
import zipfile
from io import BytesIO
from typing import Annotated

import geopandas as gpd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, iemapp

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    sts: Annotated[AwareDatetime | None, Field(description="Start Time")] = (
        None
    )
    ets: Annotated[AwareDatetime | None, Field(description="End Time")] = None
    year1: int = Field(None, description="Start Time Year")
    year2: int = Field(None, description="End Time Year")
    month1: int = Field(None, description="Start Time Month")
    month2: int = Field(None, description="End Time Month")
    day1: int = Field(None, description="Start Time Day")
    day2: int = Field(None, description="End Time Day")
    hour1: int = Field(0, description="Start Time Hour")
    hour2: int = Field(0, description="End Time Hour")
    minute1: int = Field(0, description="Start Time Minute")
    minute2: int = Field(0, description="End Time Minute")


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do something!"""
    query: Schema = environ["_cgimodel_schema"]
    if query.sts is None or query.ets is None:
        raise IncompleteWebRequest("Missing start time GET params")
    if query.sts > query.ets:
        query.sts, query.ets = query.ets, query.sts
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PROD_ID": "str:35",
            "YEAR": "int",
            "NUM": "int",
            "CONCERN": "str:64",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            sql_helper(
                """
    select to_char(issue {common}) as issue,
    to_char(expire {common}) as expire,
    product_id as prod_id, year, num,
    concerning as concern, geom
    from mpd WHERE issue >= :sts and
    issue < :ets ORDER by issue ASC""",
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
        return [b"ERROR: no results found for your query"]
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"mpd_{query.sts:%Y%m%d%H%M}_{query.ets:%Y%m%d%H%M}"

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

    return [zio.getvalue()]
