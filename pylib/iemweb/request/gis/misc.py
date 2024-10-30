""".. title:: NWS Miscellaneous Polygons

Return to `User Frontend </request/gis/misc.phtml>`_ or
`IEM API Services </api/#cgi>`_.

Documentation for /cgi-bin/request/gis/misc.py
-------------------------------------------------

This service emits polygons associated with miscellaneous NWS products, not
including SPS or those with VTEC.  The output formats are Shapefile, KML,
CSV, or Excel.  The default output format is Shapefile.

Changelog
---------

- 2024-10-31: Initial implementation.

Example Requests
----------------

Provide all miscellaneous polygons for October 2024 in shapefile and then KML
and then CSV and then Excel.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/misc.py\
?sts=2024-10-01T00:00Z&ets=2024-11-01T00:00Z

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/misc.py\
?sts=2024-10-01T00:00Z&ets=2024-11-01T00:00Z&format=kml

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/misc.py\
?sts=2024-10-01T00:00Z&ets=2024-11-01T00:00Z&format=csv

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/misc.py\
?sts=2024-10-01T00:00Z&ets=2024-11-01T00:00Z&format=excel

"""

# Local
import tempfile
import zipfile
from io import BytesIO, StringIO

# Third Party
import fiona
import geopandas as gpd
import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    format: str = Field(
        default="shp",
        description="Output format, either shp, kml, csv, or excel",
        pattern="^(shp|kml|csv|excel)$",
    )
    sts: AwareDatetime = Field(default=None, description="Start Time")
    ets: AwareDatetime = Field(default=None, description="End Time")
    year1: int = Field(default=None, description="Start Year, if sts not set")
    month1: int = Field(
        default=None, description="Start Month, if sts not set"
    )
    day1: int = Field(default=None, description="Start Day, if sts not set")
    hour1: int = Field(default=None, description="Start Hour, if sts not set")
    minute1: int = Field(
        default=None, description="Start Minute, if sts not set"
    )
    year2: int = Field(default=None, description="End Year, if ets not set")
    month2: int = Field(default=None, description="End Month, if ets not set")
    day2: int = Field(default=None, description="End Day, if ets not set")
    hour2: int = Field(default=None, description="End Hour, if ets not set")
    minute2: int = Field(
        default=None, description="End Minute, if ets not set"
    )


def run(ctx, start_response):
    """Do something!"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            text("""
                select pil, geom,
                issue at time zone 'UTC' as issue,
                expire at time zone 'UTC' as expire,
                product_id as PROD_ID
                from text_products WHERE issue >= :sts and
                issue < :ets ORDER by issue ASC
                 """),
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
    for col in ["issue", "expire"]:
        df[col] = df[col].dt.strftime(ISO8601)
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"misc_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"
    if ctx["format"] == "kml":
        fp = BytesIO()
        with fiona.drivers():
            df.to_file(fp, driver="KML", NameField="NAME", engine="fiona")
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.kml"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue()
    if ctx["format"] == "csv":
        fp = StringIO()
        df.drop(columns="geom").to_csv(fp, index=False)
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue().encode("ascii")
    if ctx["format"] == "excel":
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
            "PIL": "str:6",
            "ISSUE": "str:20",
            "EXPIRE": "str:20",
            "PROD_ID": "str:36",
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
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("GET start or end time parameters missing")
    return [run(environ, start_response)]
