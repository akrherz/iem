"""
Dump storm attributes from the database to a shapefile for the users
"""

import datetime
import zipfile
from io import BytesIO, StringIO

# import cgitb
import shapefile
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_dbconn
from pyiem.webutil import ensure_list, iemapp


def get_context(environ):
    """Figure out the CGI variables passed to this script"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing.")
    radar = ensure_list(environ, "radar")

    fmt = environ.get("fmt", "shp")

    return dict(sts=environ["sts"], ets=environ["ets"], radar=radar, fmt=fmt)


def run(ctx, start_response):
    """Do something!"""
    sio = StringIO()
    pgconn = get_dbconn("radar")
    cursor = pgconn.cursor()

    # Need to limit what we are allowing them to request as the file would get
    # massive.  So lets set arbitrary values of
    # 1) If 2 or more RADARs, less than 7 days
    if len(ctx["radar"]) == 1:
        ctx["radar"].append("XXX")
    radarlimit = ""
    if "ALL" not in ctx["radar"]:
        radarlimit = f" and nexrad in {tuple(ctx['radar'])} "
    if len(ctx["radar"]) > 2 and (ctx["ets"] - ctx["sts"]).days > 6:
        ctx["ets"] = ctx["sts"] + datetime.timedelta(days=7)

    cursor.execute(
        f"""
        SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as utctime,
        storm_id, nexrad, azimuth, range, tvs, meso, posh, poh, max_size,
        vil, max_dbz, max_dbz_height, top, drct, sknt,
        ST_y(geom) as lat, ST_x(geom) as lon
        from nexrad_attributes_log WHERE
        valid >= %s and valid < %s {radarlimit} ORDER by valid ASC
        """,
        (ctx["sts"], ctx["ets"]),
    )
    if cursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        return b"ERROR: no results found for your query"

    fn = f"stormattr_{ctx['sts']:%Y%m%d%H%M}_{ctx['ets']:%Y%m%d%H%M}"

    # sys.stderr.write("End SQL with rowcount %s" % (cursor.rowcount, ))
    if ctx["fmt"] == "csv":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        sio.write(
            (
                "VALID,STORM_ID,NEXRAD,AZIMUTH,RANGE,TVS,MESO,POSH,"
                "POH,MAX_SIZE,VIL,MAX_DBZ,MAZ_DBZ_H,TOP,DRCT,SKNT,LAT,LON\n"
            )
        )
        for row in cursor:
            sio.write(",".join([str(s) for s in row]) + "\n")
        return sio.getvalue().encode("ascii", "ignore")

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shp=shpio, shx=shxio, dbf=dbfio) as shp:
        # C is ASCII characters
        # N is a double precision integer limited to around 18 characters in
        #   length
        # D is for dates in the YYYYMMDD format,
        #   with no spaces or hyphens between the sections
        # F is for floating point numbers with the same length limits as N
        # L is for logical data which is stored in the shapefile's attribute
        #   table as a short integer as a 1 (true) or a 0 (false).
        # The values it can receive are 1, 0, y, n, Y, N, T, F
        # or the python builtins True and False
        shp.field("VALID", "C", 12)
        shp.field("STORM_ID", "C", 2)
        shp.field("NEXRAD", "C", 3)
        shp.field("AZIMUTH", "N", 3, 0)
        shp.field("RANGE", "N", 3, 0)
        shp.field("TVS", "C", 10)
        shp.field("MESO", "C", 10)
        shp.field("POSH", "N", 3, 0)
        shp.field("POH", "N", 3, 0)
        shp.field("MAX_SIZE", "F", 5, 2)
        shp.field("VIL", "N", 3, 0)
        shp.field("MAX_DBZ", "N", 3, 0)
        shp.field("MAX_DBZ_H", "F", 5, 2)
        shp.field("TOP", "F", 9, 2)
        shp.field("DRCT", "N", 3, 0)
        shp.field("SKNT", "N", 3, 0)
        shp.field("LAT", "F", 10, 4)
        shp.field("LON", "F", 10, 4)
        for row in cursor:
            shp.point(row[-1], row[-2])
            shp.record(*row)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="utf-8") as fh:
            zf.writestr(f"{fh}.prj", fh.read())
        zf.writestr(fn + ".shp", shpio.getvalue())
        zf.writestr(fn + ".shx", shxio.getvalue())
        zf.writestr(fn + ".dbf", dbfio.getvalue())
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)

    return zio.getvalue()


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Do something fun!"""
    ctx = get_context(environ)
    return [run(ctx, start_response)]
