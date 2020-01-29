"""Dumps Local Storm Reports on-demand for web requests."""
import datetime
import zipfile
import os
from io import BytesIO, StringIO

import shapefile
from paste.request import parse_formvars
from pyiem.util import get_dbconn


def get_time_domain(form):
    """Figure out the start and end timestamps"""
    if "recent" in form:
        # Allow for specifying a recent number of seconds
        ets = datetime.datetime.utcnow()
        seconds = abs(int(form.get("recent")))
        sts = ets - datetime.timedelta(seconds=seconds)
        return sts, ets

    if "year" in form:
        year1 = int(form.get("year"))
        year2 = int(form.get("year"))
    else:
        year1 = int(form.get("year1"))
        year2 = int(form.get("year2"))
    month1 = int(form.get("month1"))
    month2 = int(form.get("month2"))
    day1 = int(form.get("day1"))
    day2 = int(form.get("day2"))
    hour1 = int(form.get("hour1"))
    hour2 = int(form.get("hour2"))
    minute1 = int(form.get("minute1"))
    minute2 = int(form.get("minute2"))
    sts = datetime.datetime(year1, month1, day1, hour1, minute1)
    ets = datetime.datetime(year2, month2, day2, hour2, minute2)

    return sts, ets


def application(environ, start_response):
    """Go Main Go"""
    if environ["REQUEST_METHOD"] == "OPTIONS":
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        return [b"Allow: GET,POST,OPTIONS"]

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    # Get CGI vars
    form = parse_formvars(environ)

    (sTS, eTS) = get_time_domain(form)

    wfoLimiter = ""
    if "wfo[]" in form:
        aWFO = form.getall("wfo[]")
        aWFO.append("XXX")  # Hack to make next section work
        if "ALL" not in aWFO:
            wfoLimiter = " and wfo in %s " % (str(tuple(aWFO)),)

    os.chdir("/tmp")
    fn = "lsr_%s_%s" % (sTS.strftime("%Y%m%d%H%M"), eTS.strftime("%Y%m%d%H%M"))
    for suffix in ["shp", "shx", "dbf", "csv"]:
        if os.path.isfile("%s.%s" % (fn, suffix)):
            os.remove("%s.%s" % (fn, suffix))

    csv = StringIO()
    csv.write(
        (
            "VALID,VALID2,LAT,LON,MAG,WFO,TYPECODE,TYPETEXT,CITY,"
            "COUNTY,STATE,SOURCE,REMARK\n"
        )
    )

    cursor.execute(
        """
        SELECT distinct
        to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as dvalid,
        magnitude, wfo, type, typetext,
        city, county, state, source, substr(remark,0,200) as tremark,
        ST_y(geom), ST_x(geom),
        to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as dvalid2
        from lsrs WHERE
        valid >= '%s+00' and valid < '%s+00' %s
        ORDER by dvalid ASC
        """
        % (
            sTS.strftime("%Y-%m-%d %H:%M"),
            eTS.strftime("%Y-%m-%d %H:%M"),
            wfoLimiter,
        )
    )

    if cursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"No results found for query."]

    shpio = BytesIO()
    shxio = BytesIO()
    dbfio = BytesIO()

    with shapefile.Writer(shp=shpio, shx=shxio, dbf=dbfio) as shp:
        shp.field("VALID", "C", 12)
        shp.field("MAG", "F", 5, 2)
        shp.field("WFO", "C", 3)
        shp.field("TYPECODE", "C", 1)
        shp.field("TYPETEXT", "C", 40)
        shp.field("CITY", "C", 40)
        shp.field("COUNTY", "C", 40)
        shp.field("STATE", "C", 2)
        shp.field("SOURCE", "C", 40)
        shp.field("REMARK", "C", 200)
        shp.field("LAT", "F", 7, 4)
        shp.field("LON", "F", 9, 4)
        for row in cursor:
            row = list(row)
            shp.point(row[-2], row[-3])
            if row[9] is not None:
                row[9] = (
                    row[9]
                    .encode("utf-8", "ignore")
                    .decode("ascii", "ignore")
                    .replace(",", "_")
                )
            shp.record(*row[:-1])
            csv.write(
                ("%s,%s,%.2f,%.2f,%s,%s,%s,%s,%s,%s,%s,%s,%s\n")
                % (
                    row[0],
                    row[12],
                    row[-3],
                    row[-2],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5].encode("utf-8", "ignore").decode("ascii", "ignore"),
                    row[6],
                    row[7],
                    row[8],
                    row[9] if row[9] is not None else "",
                )
            )

    if "justcsv" in form:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=%s.csv" % (fn,)),
        ]
        start_response("200 OK", headers)
        return [csv.getvalue().encode("ascii", "ignore")]

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        zf.writestr(
            fn + ".prj", open(("/opt/iem/data/gis/meta/4326.prj")).read()
        )
        zf.writestr(fn + ".shp", shpio.getvalue())
        zf.writestr(fn + ".shx", shxio.getvalue())
        zf.writestr(fn + ".dbf", dbfio.getvalue())
        zf.writestr(fn + ".csv", csv.getvalue())
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=%s.zip" % (fn,)),
    ]
    start_response("200 OK", headers)
    return [zio.getvalue()]
