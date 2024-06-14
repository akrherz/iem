""".. title:: Download SPC Convective and Fire Weather or WPC ERO Outlooks

Documentation for /cgi-bin/request/gis/spc_outlooks.py
------------------------------------------------------

This application allows for the download of SPC Convective and Fire Weather
or WPC Excessive Rainfall Outlooks in shapefile format.

Changelog
---------

- 2024-06-14: Initial documentation of this backend

Example Requests
----------------

Provide all of the day 2 convective outlooks for the year 2024:

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/spc_outlooks.py?d=2&\
type=C&sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z

"""

# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import geopandas as gpd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    d: ListOrCSVType = Field(
        [1, 2, 3, 4, 5, 6, 7, 8], description="Days to include"
    )
    ets: AwareDatetime = Field(
        None, description="End of the period to include"
    )
    geom: str = Field(
        "geom_layers",
        description=(
            "Express geometries either as layers or non-overlapping "
            "geometries."
        ),
        pattern="geom_layers|geom",
    )
    sts: AwareDatetime = Field(
        None, description="Start of the period to include"
    )
    type: ListOrCSVType = Field(
        ["C", "F"], description="Outlook types to include"
    )
    year1: int = Field(None, description="Start year when sts is not set.")
    month1: int = Field(None, description="Start month when sts is not set.")
    day1: int = Field(None, description="Start day when sts is not set.")
    hour1: int = Field(None, description="Start hour when sts is not set.")
    minute1: int = Field(None, description="Start minute when sts is not set.")
    year2: int = Field(None, description="End year when ets is not set.")
    month2: int = Field(None, description="End month when ets is not set.")
    day2: int = Field(None, description="End day when ets is not set.")
    hour2: int = Field(None, description="End hour when ets is not set.")
    minute2: int = Field(None, description="End minute when ets is not set.")


def get_context(environ):
    """Figure out the CGI variables passed to this script"""
    types = [x[0].upper() for x in environ["type"]]
    days = [int(x) for x in environ["d"]]
    return {
        "sts": environ["sts"],
        "ets": environ["ets"],
        "types": types,
        "days": days,
        "geom_col": environ["geom"],
    }


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "MultiPolygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PRODISS": "str:12",
            "TYPE": "str:1",
            "DAY": "int",
            "THRESHOLD": "str:4",
            "CATEGORY": "str:48",  # 43 as checked max, to save space
            "CYCLE": "int",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            text(f"""select
            to_char(issue {common}) as issue,
            to_char(expire {common}) as expire,
            to_char(product_issue {common}) as prodiss,
            outlook_type as type, day, threshold, category, cycle,
            {ctx["geom_col"]} as geom
            from spc_outlooks WHERE product_issue >= :sts and
            product_issue < :ets and outlook_type = ANY(:types)
            and day = ANY(:days)
            ORDER by product_issue ASC
            """),
            conn,
            params={
                "sts": ctx["sts"],
                "ets": ctx["ets"],
                "types": ctx["types"],
                "days": ctx["days"],
            },
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"outlooks_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    with tempfile.TemporaryDirectory() as tmpdir:
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema)

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
        raise IncompleteWebRequest("GET start/end time parameters missing")
    ctx = get_context(environ)
    return [run(ctx, start_response)]
