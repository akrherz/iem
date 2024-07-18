""".. title:: Storm Prediction Center Mesoscale Convective Discussion

Documentation for /cgi-bin/request/gis/spc_mcd.py
-------------------------------------------------

The IEM archives Storm Prediction Center Mesoscale Convective Discussions (MCD)
in real-time and makes them available for download via this service.  The
raw product text is not emitted here, but the ``prod_id`` is included, which
is a reference to the raw product text.

Changelog
---------

- 2024-05-29: Initial documentation

Example Usage
-------------

Return all MCDs for 2023

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/spc_mcd.py?\
sts=2023-01-01T00:00Z&ets=2024-01-01T00:00Z

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

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    sts: AwareDatetime = Field(None, description="Start Time")
    ets: AwareDatetime = Field(None, description="End Time")
    year1: int = Field(
        None, description="Start UTC Year when sts is not provided"
    )
    year2: int = Field(
        None, description="End UTC Year when ets is not provided"
    )
    month1: int = Field(
        None, description="Start UTC Month when sts is not provided"
    )
    month2: int = Field(
        None, description="End UTC Month when ets is not provided"
    )
    day1: int = Field(
        None, description="Start UTC Day when sts is not provided"
    )
    day2: int = Field(None, description="End UTC Day when ets is not provided")
    hour1: int = Field(
        None, description="Start UTC Hour when sts is not provided"
    )
    hour2: int = Field(
        None, description="End UTC Hour when ets is not provided"
    )
    minute1: int = Field(
        None, description="Start UTC Minute when sts is not provided"
    )
    minute2: int = Field(
        None, description="End UTC Minute when ets is not provided"
    )


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "ISSUE": "str:12",
            "EXPIRE": "str:12",
            "PROD_ID": "str:35",
            "YEAR": "int",
            "NUM": "int",
            "CONFIDEN": "int",
            "CONCERN": "str:64",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            "select "
            f"to_char(issue {common}) as issue, "
            f"to_char(expire {common}) as expire, "
            "product_id as prod_id, year, num, watch_confidence as confiden, "
            "concerning as concern, geom "
            "from mcd WHERE issue >= %s and "
            "issue < %s ORDER by issue ASC",
            conn,
            params=(
                ctx["sts"],
                ctx["ets"],
            ),
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"mcd_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

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
        raise IncompleteWebRequest("GET sts/ets parameter not provided")
    if environ["sts"] > environ["ets"]:
        environ["sts"], environ["ets"] = environ["ets"], environ["sts"]
    ctx = {
        "sts": environ["sts"],
        "ets": environ["ets"],
    }
    return [run(ctx, start_response)]
