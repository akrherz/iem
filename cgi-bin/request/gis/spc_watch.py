""".. title:: Download SPC Watch Polygons and Metadata

Documentation for /cgi-bin/request/gis/spc_watch.py
---------------------------------------------------

The IEM archives the Storm Prediction Center (SPC) watch polygons and
associated metadata.  Please note that these polygons are no longer the
official watch geography with watch-by-county being the official product.
These polygons are still generally useful and somewhat accurate to the actual
watch geographic extent.

Changelog
---------

- 2024-06-09: Initial Documentation

Example Usage
-------------

Return all watch polygons for UTC 2024 in GeoJSON.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/spc_watch.py?\
sts=2024-01-01T00:00:00Z&ets=2025-01-01T00:00:00Z&format=geojson

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

    ets: AwareDatetime = Field(None, description="End Time")
    format: str = Field("shp", description="Output format")
    sts: AwareDatetime = Field(None, description="Start Time")
    year1: int = Field(None, description="Start year when sts is not provided")
    year2: int = Field(None, description="End year when ets is not provided")
    month1: int = Field(
        None, description="Start month when sts is not provided"
    )
    month2: int = Field(None, description="End month when ets is not provided")
    day1: int = Field(None, description="Start day when sts is not provided")
    day2: int = Field(None, description="End day when ets is not provided")
    hour1: int = Field(None, description="Start hour when sts is not provided")
    hour2: int = Field(None, description="End hour when ets is not provided")
    minute1: int = Field(
        None, description="Start minute when sts is not provided"
    )
    minute2: int = Field(
        None, description="End minute when ets is not provided"
    )


def start_headers(start_response, ctx, fn):
    """Figure out the proper headers for the output"""
    suffix = "zip" if ctx["format"] == "shp" else ctx["format"]
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.{suffix}"),
    ]
    start_response("200 OK", headers)


def run(environ, start_response):
    """Do something!"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start or end time")
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "MultiPolygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "SEL": "str:5",
            "TYPE": "str:3",
            "NUM": "int",
            "P_TORTWO": "int",
            "P_TOREF2": "int",
            "P_WIND10": "int",
            "P_WIND65": "int",
            "P_HAIL10": "int",
            "P_HAIL2I": "int",
            "P_HAILWND": "int",
            "MAX_HAIL": "float",
            "MAX_GUST": "int",
            "MAX_TOPS": "int",
            "MV_DRCT": "int",
            "MV_SKNT": "int",
            "IS_PDS": "bool",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            text(f"""select
            to_char(issued {common}) as issue,
            to_char(expired {common}) as expire,
            sel, type, num, geom,
            tornadoes_2m as p_tortwo, tornadoes_1m_strong as p_toref2,
            wind_10m as p_wind10, wind_1m_65kt as p_wind65,
            hail_10m as p_hail10, hail_1m_2inch as p_hail2i,
            hail_wind_6m as p_hailwnd, max_hail_size as max_hail,
            max_wind_gust_knots as max_gust, max_tops_feet as max_tops,
            storm_motion_drct as mv_drct, storm_motion_sknt as mv_sknt,
            is_pds
            from watches WHERE issued >= :sts and
            issued < :ets ORDER by issued ASC
            """),
            conn,
            params={
                "sts": environ["sts"],
                "ets": environ["ets"],
            },
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"watches_{environ['sts']:%Y%m%d%H%M}_{environ['ets']:%Y%m%d%H%M}"
    start_headers(start_response, environ, fn)
    if environ["format"] == "csv":
        return df.to_csv(index=False).encode("utf-8")
    if environ["format"] == "geojson":
        with tempfile.NamedTemporaryFile("w", delete=True) as tmp:
            df.to_file(tmp.name, driver="GeoJSON")
            with open(tmp.name, encoding="utf8") as fh:
                res = fh.read()
        return res.encode("utf-8")
    if environ["format"] == "kml":
        df["NAME"] = (
            df["ISSUE"].str.slice(0, 4)
            + ": "
            + df["TYPE"]
            + " #"
            + df["NUM"].apply(str)
        )
        fp = BytesIO()
        with fiona.drivers():
            df.to_file(fp, driver="KML", NameField="NAME")
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

    return zio.getvalue()


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do something fun!"""
    return [run(environ, start_response)]
