"""Provide PIREPs."""
import datetime
import zipfile
from io import BytesIO, StringIO

import shapefile
from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc


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
        (ets, sts) = (sts, ets)

    form["fmt"] = form.get("fmt", "shp")
    form["sts"] = sts
    form["ets"] = ets

    return form


def run(ctx, start_response):
    """Go run!"""
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
        substr(aircraft_type, 0, 40),
        substr(replace(report, ',', ' '), 0, 255),
        ST_y(geom::geometry) as lat, ST_x(geom::geometry) as lon
        from pireps WHERE {spatialsql}
        valid >= %s and valid < %s ORDER by valid ASC
        """
    args = (
        ctx["sts"],
        ctx["ets"],
    )

    cursor.execute(sql, args)
    if cursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"

    fn = f"pireps_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    # sys.stderr.write("End SQL with rowcount %s" % (cursor.rowcount, ))
    if ctx["fmt"] == "csv":
        sio = StringIO()
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        sio.write("VALID,URGENT,AIRCRAFT,REPORT,LAT,LON\n")
        for row in cursor:
            sio.write(",".join([str(s) for s in row]) + "\n")
        return sio.getvalue().encode("ascii", "ignore")

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shx=shxio, dbf=dbfio, shp=shpio) as shp:
        shp.field("VALID", "C", 12)
        shp.field("URGENT", "C", 1)
        shp.field("AIRCRAFT", "C", 40)
        shp.field("REPORT", "C", 255)  # Max field size is 255
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
    start_response("200 OK", headers)
    return zio.getvalue()


def application(environ, start_response):
    """Do something fun!"""
    ctx = get_context(environ)
    return [run(ctx, start_response)]
