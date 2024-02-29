"""Dump SPC Watches."""

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

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


def get_context(environ):
    """Figure out the CGI variables passed to this script"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")

    return dict(
        sts=environ["sts"],
        ets=environ["ets"],
        format=environ.get("format", "shp"),
    )


def start_headers(start_response, ctx, fn):
    """Figure out the proper headers for the output"""
    suffix = "zip" if ctx["format"] == "shp" else ctx["format"]
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.{suffix}"),
    ]
    start_response("200 OK", headers)


def run(ctx, start_response):
    """Do something!"""
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
            "select "
            f"to_char(issued {common}) as issue, "
            f"to_char(expired {common}) as expire, "
            "sel, type, num, geom, "
            "tornadoes_2m as p_tortwo, tornadoes_1m_strong as p_toref2, "
            "wind_10m as p_wind10, wind_1m_65kt as p_wind65, "
            "hail_10m as p_hail10, hail_1m_2inch as p_hail2i, "
            "hail_wind_6m as p_hailwnd, max_hail_size as max_hail, "
            "max_wind_gust_knots as max_gust, max_tops_feet as max_tops, "
            "storm_motion_drct as mv_drct, storm_motion_sknt as mv_sknt, "
            "is_pds "
            "from watches WHERE issued >= %s and "
            "issued < %s ORDER by issued ASC",
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
    fn = f"watches_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"
    start_headers(start_response, ctx, fn)
    if ctx["format"] == "csv":
        return df.to_csv(index=False).encode("utf-8")
    if ctx["format"] == "geojson":
        with tempfile.NamedTemporaryFile("w", delete=True) as tmp:
            df.to_file(tmp.name, driver="GeoJSON")
            with open(tmp.name, encoding="utf8") as fh:
                res = fh.read()
        return res.encode("utf-8")
    if ctx["format"] == "kml":
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
        df.to_file(f"{tmpdir}/{fn}.shp", schema=schema)

        zio = BytesIO()
        with zipfile.ZipFile(
            zio, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            with open(PRJFILE, encoding="utf-8") as fh:
                zf.writestr(f"{fn}.prj", fh.read())
            for suffix in ["shp", "shx", "dbf"]:
                zf.write(f"{tmpdir}/{fn}.{suffix}", f"{fn}.{suffix}")

    return zio.getvalue()


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Do something fun!"""
    ctx = get_context(environ)
    return [run(ctx, start_response)]
