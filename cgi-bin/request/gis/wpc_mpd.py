"""Dump WPC MPDs."""
# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import geopandas as gpd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import iemapp

# cgitb.enable()
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Do something!"""
    if "sts" not in environ:
        raise IncompleteWebRequest("Missing start time GET params")
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
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"mpd_{environ['sts']:%Y%m%d%H%M}_{environ['ets']:%Y%m%d%H%M}"

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

    return [zio.getvalue()]
