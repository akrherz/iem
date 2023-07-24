"""Dump WPC MPDs."""
# Local
import tempfile
import zipfile
from io import BytesIO

# Third Party
import geopandas as gpd
from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn, utc

# cgitb.enable()
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

    return dict(sts=sts, ets=ets)


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "Polygon",
        "properties": dict(
            [
                ("ISSUE", "str:12"),
                ("EXPIRE", "str:12"),
                ("PROD_ID", "str:35"),
                ("YEAR", "int"),
                ("NUM", "int"),
                ("CONCERN", "str:64"),
            ]
        ),
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
                ctx["sts"],
                ctx["ets"],
            ),
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"mpd_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

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


def application(environ, start_response):
    """Do something fun!"""
    ctx = get_context(environ)
    return [run(ctx, start_response)]
