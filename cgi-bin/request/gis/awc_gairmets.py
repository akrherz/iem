"""Dump AWC G-AIRMETs."""
# Local
import os
import zipfile
from io import BytesIO

# Third Party
import fiona
import geopandas as gpd
from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn, utc

# cgitb.enable()
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


def run(ctx, start_response):
    """Do something!"""
    common = "at time zone 'UTC', 'YYYY-MM-DD\"T\"HH24:MI:00\"Z\"'"
    schema = {
        "geometry": "Polygon",
        "properties": dict(
            [
                ("NAME", "str:64"),
                ("LABEL", "str:4"),
                ("GML_ID", "str:32"),
                ("VALID_AT", "str:20"),
                ("VALID_FM", "str:20"),
                ("VALID_TO", "str:20"),
                ("ISSUTIME", "str:20"),
                ("PROD_ID", "str:36"),
                ("STATUS", "str:32"),
                ("HZTYPE", "str:256"),
                ("WXCOND", "str:256"),
            ]
        ),
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
