"""Dumps Local Storm Reports on-demand for web requests."""
import datetime
import zipfile
import os
from io import BytesIO, StringIO

import shapefile
import pandas as pd
from pandas.io.sql import read_sql
from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ISO8660 = "%Y-%m-%dT%H:%M"


def get_time_domain(form):
    """Figure out the start and end timestamps"""
    if "recent" in form:
        # Allow for specifying a recent number of seconds
        ets = utc()
        seconds = abs(int(form.get("recent")))
        sts = ets - datetime.timedelta(seconds=seconds)
        return sts, ets

    if "sts" in form and "ets" in form:
        sts = datetime.datetime.strptime(form.get("sts")[:16], ISO8660)
        ets = datetime.datetime.strptime(form.get("ets")[:16], ISO8660)
        return (
            sts.replace(tzinfo=datetime.timezone.utc),
            ets.replace(tzinfo=datetime.timezone.utc),
        )
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
    sts = utc(year1, month1, day1, hour1, minute1)
    ets = utc(year2, month2, day2, hour2, minute2)

    return sts, ets


def do_excel(pgconn, sts, ets, wfolimiter):
    """Export as Excel."""
    df = read_sql(
        "WITH wfos as (select case when length(id) = 4 then substr(id, 1, 3) "
        "else id end as cwa, tzname from stations where network = 'WFO') "
        "SELECT distinct "
        "l.wfo as office, "
        "to_char(valid at time zone w.tzname, "
        " 'YYYY/MM/DD HH24:MI') as lvalid, "
        "to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as utcvalid, "
        "county, city, state, typetext, magnitude, source, "
        "ST_y(geom) as lat, ST_x(geom) as lon, coalesce(remark, '') as remark "
        "from lsrs l JOIN wfos w on (l.wfo = w.cwa) "
        f"WHERE valid >= %s and valid < %s {wfolimiter} ORDER by utcvalid ASC",
        pgconn,
        params=(sts, ets),
    )
    df = df.rename(
        {
            "office": "Office",
            "lvalid": "Report Time (Local WFO Timezone)",
            "utcvalid": "Report Time (UTC Timezone)",
            "county": "County",
            "city": "Location",
            "state": "ST",
            "typetext": "Event Type",
            "magnitude": "Mag.",
            "source": "Source",
            "lat": "Lat",
            "lon": "Lon",
            "remark": "Remark",
        },
        axis=1,
    )
    bio = BytesIO()
    # pylint: disable=abstract-class-instantiated
    writer = pd.ExcelWriter(bio, engine="xlsxwriter")
    df.to_excel(writer, "Local Storm Reports", index=False)
    worksheet = writer.sheets["Local Storm Reports"]
    worksheet.set_column("B:C", 36)
    worksheet.set_column("D:E", 24)
    worksheet.set_column("G:G", 24)
    worksheet.set_column("I:I", 24)
    worksheet.set_column("L:L", 100)
    worksheet.freeze_panes(1, 0)
    writer.close()
    return bio.getvalue()


def application(environ, start_response):
    """Go Main Go"""
    if environ["REQUEST_METHOD"] == "OPTIONS":
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        return [b"Allow: GET,POST,OPTIONS"]

    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    # Get CGI vars
    form = parse_formvars(environ)

    (sts, ets) = get_time_domain(form)

    wfoLimiter = ""
    if "wfo[]" in form:
        aWFO = form.getall("wfo[]")
        aWFO.append("XXX")  # Hack to make next section work
        if "ALL" not in aWFO:
            wfoLimiter = " and wfo in %s " % (str(tuple(aWFO)),)

    fn = "lsr_%s_%s" % (sts.strftime("%Y%m%d%H%M"), ets.strftime("%Y%m%d%H%M"))
    if form.get("fmt", "") == "excel":
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}.xlsx"),
        ]
        start_response("200 OK", headers)
        return [do_excel(pgconn, sts, ets, wfoLimiter)]

    os.chdir("/tmp")
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
        f"""
        SELECT distinct
        to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as dvalid,
        magnitude, wfo, type, typetext,
        city, county, state, source,
        substr(coalesce(remark, ''),0,200) as tremark,
        ST_y(geom), ST_x(geom),
        to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as dvalid2
        from lsrs WHERE
        valid >= %s and valid < %s {wfoLimiter}
        ORDER by dvalid ASC
        """,
        (sts, ets),
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

    if "justcsv" in form or form.get("fmt", "") == "csv":
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
