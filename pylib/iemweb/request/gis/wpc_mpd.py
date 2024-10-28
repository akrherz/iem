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

Provide a shapefile of WPC MPDs for July 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/wpc_mpd.py?\
sts=2024-07-01T00:00Z&ets=2024-08-01T00:00Z

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
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start time GET params")
    if environ["sts"] > environ["ets"]:
        environ["sts"], environ["ets"] = environ["ets"], environ["sts"]
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
            "select "
            f"to_char(issue {common}) as issue, "
            f"to_char(expire {common}) as expire, "
            "product_id as prod_id, year, num, "
            "concerning as concern, geom "
            "from mpd WHERE issue >= %s and "
            "issue < %s ORDER by issue ASC",
            conn,
            params=(
                environ["sts"],
                environ["ets"],
            ),
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: no results found for your query"]
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"mpd_{environ['sts']:%Y%m%d%H%M}_{environ['ets']:%Y%m%d%H%M}"

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
