"""Dump AWC G-AIRMETs."""

# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import fiona
import geopandas as gpd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import iemapp

# cgitb.enable()
fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


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
            df.to_file(fp, driver="KML", NameField="NAME")
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.kml"),
        ]
        start_response("200 OK", headers)
        return fp.getvalue()

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


@iemapp(default_tz="UTC")
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
