"""Dump SPC Watches."""
# Local
from io import BytesIO
import os
import tempfile
import zipfile

# Third Party
import fiona
import geopandas as gpd
from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn, utc

fiona.supported_drivers["KML"] = "rw"
PRJFILE = "/opt/iem/data/gis/meta/4326.prj"


def get_context(environ):
    """Figure out the CGI variables passed to this script"""
    form = parse_formvars(environ)
    if "year" in form:
        year1 = form.get("year")
        year2 = year1
    else:
        year1 = form.get("year1")
        year2 = form.get("year2")
    month1 = form.get("month1")
    month2 = form.get("month2")
    day1 = form.get("day1")
    day2 = form.get("day2")
    hour1 = form.get("hour1")
    hour2 = form.get("hour2")
    minute1 = form.get("minute1")
    minute2 = form.get("minute2")

    sts = utc(int(year1), int(month1), int(day1), int(hour1), int(minute1))
    ets = utc(int(year2), int(month2), int(day2), int(hour2), int(minute2))
    if ets < sts:
        sts, ets = ets, sts

    return dict(sts=sts, ets=ets, format=form.get("format", "shp"))


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
        "properties": dict(
            [
                ("ISSUE", "str:12"),
                ("EXPIRE", "str:12"),
                ("SEL", "str:5"),
                ("TYPE", "str:3"),
                ("NUM", "int"),
                ("P_TORTWO", "int"),
                ("P_TOREF2", "int"),
                ("P_WIND10", "int"),
                ("P_WIND65", "int"),
                ("P_HAIL10", "int"),
                ("P_HAIL2I", "int"),
                ("P_HAILWND", "int"),
                ("MAX_HAIL", "float"),
                ("MAX_GUST", "int"),
                ("MAX_TOPS", "int"),
                ("MV_DRCT", "int"),
                ("MV_SKNT", "int"),
                ("IS_PDS", "bool"),
            ]
        ),
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

    os.chdir("/tmp")
    df.to_file(f"{fn}.shp", schema=schema)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open(PRJFILE, encoding="utf-8") as fh:
            zf.writestr(f"{fn}.prj", fh.read())
        for suffix in ["shp", "shx", "dbf"]:
            zf.write(f"{fn}.{suffix}")
    for suffix in ["shp", "shx", "dbf"]:
        os.unlink(f"{fn}.{suffix}")

    return zio.getvalue()


def application(environ, start_response):
    """Do something fun!"""
    ctx = get_context(environ)
    return [run(ctx, start_response)]
