"""Dump SPC Outlooks."""

# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import geopandas as gpd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import iemapp

PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


def get_context(environ):
    """Figure out the CGI variables passed to this script"""
    artypes = environ.get("type", [])
    if not isinstance(artypes, list):
        artypes = [artypes]
    types = [x[0].upper() for x in artypes]
    if not types:
        types = ["C", "F"]
    ard = environ.get("d", [])
    if not isinstance(ard, list):
        ard = [ard]
    days = [int(x) for x in ard]
    if not days:
        days = list(range(1, 9))
    return {
        "sts": environ["sts"],
        "ets": environ["ets"],
        "types": types,
        "days": days,
        "geom_col": "geom" if environ.get("geom") == "geom" else "geom_layers",
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
            f"""select
            to_char(issue {common}) as issue,
            to_char(expire {common}) as expire,
            to_char(product_issue {common}) as prodiss,
            outlook_type as type, day, threshold, category, cycle,
            {ctx["geom_col"]} as geom
            from spc_outlooks WHERE product_issue >= %s and
            product_issue < %s and outlook_type = ANY(%s) and day = ANY(%s)
            ORDER by product_issue ASC
            """,
            conn,
            params=(
                ctx["sts"],
                ctx["ets"],
                ctx["types"],
                ctx["days"],
            ),
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


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Do something fun!"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")
    ctx = get_context(environ)
    return [run(ctx, start_response)]
