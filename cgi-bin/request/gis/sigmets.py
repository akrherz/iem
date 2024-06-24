""".. title:: SIGMET Data Service

Documentation for /cgi-bin/request/gis/sigmets.py
-------------------------------------------------

This service emits Shapefiles or KML of SIGMET data for a given time period.

CGI Parameters
--------------

- `{year,month,day,hour,min}1`: The start time of the data request in UTC.
- `{year,month,day,hour,min}2`: The end time of the data request in UTC.
- `format`: The format of the output, either `shp` or `kml`.

"""

# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import fiona
import geopandas as gpd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import iemapp

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:00\"Z\"'"
    schema = {
        "geometry": "Polygon",
        "properties": {
            "NAME": "str:64",
            "LABEL": "str:16",
            "TYPE": "str:1",
            "ISSUE": "str:20",
            "EXPIRE": "str:20",
        },
    }
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            f"select label  || ' ' || sigmet_type as name, label, "
            "sigmet_type as type, "
            f"to_char(issue {common}) as issue, "
            f"to_char(expire {common}) as expire, geom "
            "from sigmets_archive WHERE issue >= %s and "
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
    fn = f"sigmets_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"
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


@iemapp(default_tz="UTC", help=__doc__)
def application(environ, start_response):
    """Do something fun!"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")
    ctx = {
        "sts": environ["sts"],
        "ets": environ["ets"],
        "format": environ.get("format", "shp"),
    }
    return [run(ctx, start_response)]
