"""Dump SPS."""
# Local
import os
import tempfile
import zipfile
from io import BytesIO

# Third Party
import geopandas as gpd
from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn, utc

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
                ("PROD_ID", "str:32"),
                ("WFO", "str:3"),
                ("LNDSPOUT", "str:64"),
                ("WTRSPOUT", "str:64"),
                ("MAX_HAIL", "str:16"),
                ("MAX_WIND", "str:16"),
                ("TML_VALD", "str:12"),
                ("TML_DRCT", "int"),
                ("TML_SKNT", "int"),
            ]
        ),
    }
    with get_sqlalchemy_conn("postgis") as pgconn:
        df = gpd.read_postgis(
            "select "
            f"to_char(issue {common}) as issue, "
            f"to_char(expire {common}) as expire, "
            f"product_id as prod_id, "
            "wfo, landspout as lndspout, waterspout as wtrspout, "
            "max_hail_size as max_hail, max_wind_gust as max_wind, "
            f"to_char(tml_valid {common}) as tml_vald, "
            "tml_direction as tml_drct, "
            "tml_sknt, geom from sps WHERE issue >= %s and "
            "issue < %s and not ST_isempty(geom) ORDER by issue ASC",
            pgconn,
            params=(ctx["sts"], ctx["ets"]),
            geom_col="geom",
        )
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"
    df.columns = [s.upper() if s != "geom" else "geom" for s in df.columns]
    fn = f"sps_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    with tempfile.TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        df.to_file(f"{fn}.shp", schema=schema)

        zio = BytesIO()
        with zipfile.ZipFile(
            zio, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            with open(PRJFILE, encoding="ascii") as fp:
                zf.writestr(f"{fn}.prj", fp.read())
            zf.write(f"{fn}.shp")
            zf.write(f"{fn}.shx")
            zf.write(f"{fn}.dbf")
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
