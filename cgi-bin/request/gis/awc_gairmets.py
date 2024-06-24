""".. title:: AWC Graphical AIRMETs

Documentation for /cgi-bin/request/gis/awc_gairmets.py
------------------------------------------------------

This service emits the archive of IEM's best attempt at processing graphical
AIRMETs.

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

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


class Schema(CGIModel):
    """See how we are called."""

    format: str = Field("shp", description="Output Format")
    sts: AwareDatetime = Field(None, description="Start Time")
    ets: AwareDatetime = Field(None, description="End Time")
    year1: int = Field(
        None, description="Start Year in UTC, when sts not set."
    )
    month1: int = Field(
        None, description="Start Month in UTC, when sts not set."
    )
    day1: int = Field(None, description="Start Day in UTC, when sts not set.")
    hour1: int = Field(0, description="Start Hour in UTC, when sts not set.")
    minute1: int = Field(
        0, description="Start Minute in UTC, when sts not set."
    )
    year2: int = Field(None, description="End Year in UTC, when ets not set.")
    month2: int = Field(
        None, description="End Month in UTC, when ets not set."
    )
    day2: int = Field(None, description="End Day in UTC, when ets not set.")
    hour2: int = Field(0, description="End Hour in UTC, when ets not set.")
    minute2: int = Field(0, description="End Minute in UTC, when ets not set.")


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:00\"Z\"'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "NAME": "str:64",
            "LABEL": "str:4",
            "GML_ID": "str:32",
            "VALID_AT": "str:20",
            "VALID_FM": "str:20",
            "VALID_TO": "str:20",
            "ISSUTIME": "str:20",
            "PROD_ID": "str:36",
            "STATUS": "str:32",
            "HZTYPE": "str:256",
            "WXCOND": "str:256",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            "select label, gml_id, "
            f"gml_id  || ' ' || to_char(valid_at {common}) as name, "
            f"to_char(valid_at {common}) as valid_at, "
            f"to_char(valid_from {common}) as valid_fm, "
            f"to_char(valid_to {common}) as valid_to, "
            f"to_char(issuetime {common}) as issutime, "
            "product_id as prod_id, status, hazard_type as hztype, "
            "array_to_string(weather_conditions, ',') as wxcond, geom "
            "from airmets WHERE issuetime >= %s and "
            "issuetime < %s ORDER by valid_at ASC",
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
    fn = f"airmets_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"
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
        raise IncompleteWebRequest("Start and End Time are required!")
    ctx = {
        "sts": environ["sts"],
        "ets": environ["ets"],
        "format": environ["format"],
    }
    return [run(ctx, start_response)]
