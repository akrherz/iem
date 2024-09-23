""".. title:: Special Weather Statement (SPS) Data Service

Return to `API Services </api/#cgi>`_ or
`SPS Download Frontend </request/gis/sps.phtml>`_.

Documentation for /cgi-bin/request/gis/sps.py
---------------------------------------------

This service emits a shapefile of Special Weather Statements (SPS) data.

Changelog
---------

- 2024-09-23: Initial documentation release

Example Requests
----------------

Provide a zip file of SPS data from August 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/sps.py?\
sts=2024-08-01T00:00Z&ets=2024-09-01T00:00Z

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
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    sts: AwareDatetime = Field(
        None, description="Start timestamp for the data request"
    )
    ets: AwareDatetime = Field(
        None, description="End timestamp for the data request"
    )
    year1: int = Field(
        None, description="Start year, when sts is not provided"
    )
    month1: int = Field(
        None, description="Start month, when sts is not provided"
    )
    day1: int = Field(None, description="Start day, when sts is not provided")
    hour1: int = Field(
        None, description="Start hour, when sts is not provided"
    )
    minute1: int = Field(
        None, description="Start minute, when sts is not provided"
    )
    year2: int = Field(None, description="End year, when ets is not provided")
    month2: int = Field(
        None, description="End month, when ets is not provided"
    )
    day2: int = Field(None, description="End day, when ets is not provided")
    hour2: int = Field(None, description="End hour, when ets is not provided")
    minute2: int = Field(
        None, description="End minute, when ets is not provided"
    )


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PROD_ID": "str:36",
            "WFO": "str:3",
            "LNDSPOUT": "str:64",
            "WTRSPOUT": "str:64",
            "MAX_HAIL": "str:16",
            "MAX_WIND": "str:16",
            "TML_VALD": "str:12",
            "TML_DRCT": "int",
            "TML_SKNT": "int",
        },
    }
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = gpd.read_postgis(
            text(f"""
            select to_char(issue {common}) as issue,
            to_char(expire {common}) as expire, product_id as prod_id,
            wfo, landspout as lndspout, waterspout as wtrspout,
            max_hail_size as max_hail, max_wind_gust as max_wind,
            to_char(tml_valid {common}) as tml_vald,
            tml_direction as tml_drct,
            tml_sknt, geom from sps WHERE issue >= :sts and
            issue < :ets and not ST_isempty(geom) ORDER by issue ASC
            """),
            pgconn,
            params=ctx,
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"sps_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    with tempfile.TemporaryDirectory() as tmpdir:
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema, engine="fiona")

        zio = BytesIO()
        with zipfile.ZipFile(
            zio, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            with open(PRJFILE, encoding="ascii") as fp:
                zf.writestr(f"{fn}.prj", fp.read())
            for suffix in ("shp", "shx", "dbf"):
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
        raise IncompleteWebRequest("GET start/end timestamp params missing")
    ctx = {"sts": environ["sts"], "ets": environ["ets"]}
    return [run(ctx, start_response)]
