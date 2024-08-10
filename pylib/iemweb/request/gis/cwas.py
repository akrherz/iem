""".. title:: CWAS Data Service

Return to `user frontend </request/gis/cwas.phtml>`_

Documentation for /cgi-bin/request/gis/cwas.py
----------------------------------------------

This service emits Center Weather Advisory (CWA) polygons in either KML or
Shapefile format.

Changelog
---------

- 2024-08-10: Initital documentation update and usage of pydantic validation.

Example Requests
----------------

Provide all CWAs for 10 Aug 2024 as a shapefile or a KML file.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/cwas.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/cwas.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z&format=kml

"""

# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import fiona
import geopandas as gpd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    sts: AwareDatetime = Field(description="Start Time")
    ets: AwareDatetime = Field(description="End Time")
    format: str = Field(
        default="shp", description="Output format, either kml or shp"
    )
    year1: int = Field(
        default=None, description="Start year when sts is not provided"
    )
    month1: int = Field(
        default=None, description="Start month when sts is not provided"
    )
    day1: int = Field(
        default=None, description="Start day when sts is not provided"
    )
    hour1: int = Field(
        default=None, description="Start hour when sts is not provided"
    )
    minute1: int = Field(
        default=None, description="Start minute when sts is not provided"
    )
    year2: int = Field(
        default=None, description="End year when ets is not provided"
    )
    month2: int = Field(
        default=None, description="End month when ets is not provided"
    )
    day2: int = Field(
        default=None, description="End day when ets is not provided"
    )
    hour2: int = Field(
        default=None, description="End hour when ets is not provided"
    )
    minute2: int = Field(
        default=None, description="End minute when ets is not provided"
    )


def run(ctx, start_response):
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
            text(f"""select center,
            to_char(issue {common}) as issue,
            to_char(expire {common}) as expire,
            product_id as prod_id, narrative as narrativ, num as number,
            geom from cwas WHERE issue >= :sts and
            issue < :ets ORDER by issue ASC"""),
            conn,
            params={
                "sts": ctx["sts"],
                "ets": ctx["ets"],
            },
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"cwas_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"
    if ctx["format"] == "kml":
        fp = BytesIO()
        with fiona.drivers():
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
def application(environ, start_response):
    """Do something fun!"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("GET start time parameters missing")
    return [run(environ, start_response)]
