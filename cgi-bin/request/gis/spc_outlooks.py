"""Dump SPC Outlooks."""
# Local
from io import BytesIO
import os
import zipfile

# Third Party
from geopandas import read_postgis
from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc

# cgitb.enable()


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

    types = [x[0].upper() for x in form.getall("type")]
    if not types:
        types = ["C", "F"]
    days = [int(x) for x in form.getall("d")]
    if not days:
        days = list(range(1, 9))
    return dict(sts=sts, ets=ets, types=types, days=days)


def run(ctx, start_response):
    """Do something!"""
    pgconn = get_dbconn("postgis")
    common = "at time zone 'UTC', 'YYYYMMDDHH24MI'"
    schema = {
        "geometry": "MultiPolygon",
        "properties": dict(
            [
                ("ISSUE", "str:12"),
                ("EXPIRE", "str:12"),
                ("PRODISS", "str:12"),
                ("TYPE", "str:1"),
                ("DAY", "int"),
                ("THRESHOLD", "str:4"),
                ("CATEGORY", "str:64"),
                ("CYCLE", "int"),
            ]
        ),
    }
    df = read_postgis(
        "select "
        f"to_char(issue {common}) as issue, "
        f"to_char(expire {common}) as expire, "
        f"to_char(product_issue {common}) as prodiss, "
        "outlook_type as type, day, threshold, category, cycle, geom "
        "from spc_outlooks WHERE product_issue >= %s and "
        "product_issue < %s and outlook_type in %s and day in %s "
        "ORDER by product_issue ASC",
        pgconn,
        params=(
            ctx["sts"],
            ctx["ets"],
            tuple(ctx["types"]),
            tuple(ctx["days"]),
        ),
        geom_col="geom",
    )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = "outlooks_%s_%s" % (
        ctx["sts"].strftime("%Y%m%d%H%M"),
        ctx["ets"].strftime("%Y%m%d%H%M"),
    )

    os.chdir("/tmp")
    df.to_file(f"{fn}.shp", schema=schema)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        zf.writestr(
            fn + ".prj", open(("/opt/iem/data/gis/meta/4326.prj")).read()
        )
        zf.write(f"{fn}.shp")
        zf.write(f"{fn}.shx")
        zf.write(f"{fn}.dbf")
    for suffix in ["shp", "shx", "dbf"]:
        os.unlink(f"{fn}.{suffix}")
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=%s.zip" % (fn,)),
    ]
    start_response("200 OK", headers)

    return zio.getvalue()


def application(environ, start_response):
    """Do something fun!"""
    ctx = get_context(environ)
    return [run(ctx, start_response)]
