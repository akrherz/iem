"""Provide PIREPs."""
import datetime
import zipfile
from io import BytesIO, StringIO

import shapefile
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconn
from pyiem.webutil import ensure_list, iemapp


def get_context(environ):
    """Figure out the CGI variables passed to this script"""
    form = {}
    form["fmt"] = environ.get("fmt", "shp")
    form["sts"] = environ["sts"]
    form["ets"] = environ["ets"]
    form["artcc"] = ensure_list(environ, "artcc")
    if "_ALL" in form["artcc"]:
        form["artcc"] = []
    return form


def run(ctx, start_response):
    """Go run!"""
    artcc_sql = "" if not ctx["artcc"] else " artcc = ANY(%s) and "
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    spatialsql = ""
    if ctx.get("filter", "0") == "1":
        distance = float(ctx.get("degrees", 1.0))
        lon = float(ctx.get("lon", -91.99))
        lat = float(ctx.get("lat", 41.99))
        spatialsql = (
            f"ST_Distance(geom::geometry, ST_SetSRID(ST_Point({lon}, {lat}), "
            f"4326)) <= {distance} and "
        )
    else:
        if (ctx["ets"] - ctx["sts"]).days > 120:
            ctx["ets"] = ctx["sts"] + datetime.timedelta(days=120)
    sql = f"""
        SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
        case when is_urgent then 'T' else 'F' end,
        substr(replace(aircraft_type, ',', ' '), 0, 40),
        substr(replace(report, ',', ' '), 0, 255),
        substr(trim(substring(replace(report, ',', ' '),
            '/IC([^/]*)/')), 0, 255) as icing,
        substr(trim(substring(replace(report, ',', ' '),
            '/TB([^/]*)/')), 0, 255) as turb,
        artcc, ST_y(geom::geometry) as lat, ST_x(geom::geometry) as lon
        from pireps WHERE {spatialsql} {artcc_sql}
        valid >= %s and valid < %s ORDER by valid ASC
        """
    args = [
        ctx["sts"],
        ctx["ets"],
    ]
    if ctx["artcc"]:
        args.insert(0, ctx["artcc"])

    cursor.execute(sql, args)
    if cursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        pgconn.close()
        return b"ERROR: no results found for your query"

    fn = f"pireps_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    if ctx["fmt"] == "csv":
        sio = StringIO()
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        sio.write(
            "VALID,URGENT,AIRCRAFT,REPORT,ICING,TURBULENCE,ATRCC,LAT,LON\n"
        )
        for row in cursor:
            sio.write(",".join([str(s) for s in row]) + "\n")
        pgconn.close()
        return sio.getvalue().encode("ascii", "ignore")

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shx=shxio, dbf=dbfio, shp=shpio) as shp:
        shp.field("VALID", "C", 12)
        shp.field("URGENT", "C", 1)
        shp.field("AIRCRAFT", "C", 40)
        shp.field("REPORT", "C", 255)  # Max field size is 255
        shp.field("ICING", "C", 255)  # Max field size is 255
        shp.field("TURB", "C", 255)  # Max field size is 255
        shp.field("ARTCC", "C", 3)
        shp.field("LAT", "F", 7, 4)
        shp.field("LON", "F", 9, 4)
        for row in cursor:
            if row[-1] is None:
                continue
            shp.point(row[-1], row[-2])
            shp.record(*row)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="ascii") as fh:
            zf.writestr(f"{fn}.prj", fh.read())
        zf.writestr(f"{fn}.shp", shpio.getvalue())
        zf.writestr(f"{fn}.shx", shxio.getvalue())
        zf.writestr(f"{fn}.dbf", dbfio.getvalue())
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    pgconn.close()
    start_response("200 OK", headers)
    return zio.getvalue()


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Do something fun!"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing.")
    ctx = get_context(environ)
    return [run(ctx, start_response)]
