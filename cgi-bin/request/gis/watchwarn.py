#!/usr/bin/env python
"""Generate a shapefile of warnings based on the CGI request"""
import zipfile
import os
import cgi
import sys
import datetime

from psycopg2.extras import DictCursor
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping
from shapely.wkb import loads
from pyiem.util import get_dbconn, utc, ssw


def get_time_extent(form):
    """ Figure out the time extent of this request"""
    if "year" in form:
        year1 = form.getfirst("year")
        year2 = form.getfirst("year")
    else:
        year1 = form.getfirst("year1")
        year2 = form.getfirst("year2")
    month1 = form.getfirst("month1")
    month2 = form.getfirst("month2")
    day1 = form.getfirst("day1")
    day2 = form.getfirst("day2")
    hour1 = form.getfirst("hour1")
    hour2 = form.getfirst("hour2")
    minute1 = form.getfirst("minute1")
    minute2 = form.getfirst("minute2")
    sts = utc(int(year1), int(month1), int(day1), int(hour1), int(minute1))
    ets = utc(int(year2), int(month2), int(day2), int(hour2), int(minute2))
    return sts, ets


def char3(wfos):
    """Make sure we don't have any 4 char IDs."""
    res = []
    for wfo in wfos:
        res.append(wfo[1:] if len(wfo) == 4 else wfo)
    return res


def parse_wfo_location_group(form):
    """Parse wfoLimiter"""
    limiter = ""
    if "wfo[]" in form:
        wfos = form.getlist("wfo[]")
        wfos.append("XXX")  # Hack to make next section work
        if "ALL" not in wfos:
            limiter = " and w.wfo in %s " % (str(tuple(char3(wfos))),)

    if "wfos[]" in form:
        wfos = form.getlist("wfos[]")
        wfos.append("XXX")  # Hack to make next section work
        if "ALL" not in wfos:
            limiter = " and w.wfo in %s " % (str(tuple(char3(wfos))),)
    return limiter


def send_error(msg):
    """Error out please!"""
    ssw("Content-type: text/plain\n\n")
    ssw("ERROR: %s" % (msg,))
    sys.exit()


def main():
    """Go Main Go"""
    form = cgi.FieldStorage()
    sts, ets = get_time_extent(form)

    table_extra = ""
    location_group = form.getfirst("location_group", "wfo")
    if location_group == "states":
        if "states[]" in form:
            states = form.getlist("states[]")
            states.append("XX")  # Hack for 1 length
            wfo_limiter = (
                " and ST_Overlaps(s.the_geom, w.geom) and s.state_abbr in %s "
            ) % (tuple(states),)
            wfo_limiter2 = (" and substr(w.ugc, 1, 2) in %s ") % (
                str(tuple(states)),
            )
            table_extra = " , states s "
        else:
            send_error("No state specified")
    elif location_group == "wfo":
        wfo_limiter = parse_wfo_location_group(form)
        wfo_limiter2 = wfo_limiter
    else:
        # Unknown location_group
        send_error("Unknown location_group (%s)" % (location_group,))

    # Change to postgis db once we have the wfo list
    pgconn = get_dbconn("postgis", user="nobody")
    fn = "wwa_%s_%s" % (sts.strftime("%Y%m%d%H%M"), ets.strftime("%Y%m%d%H%M"))
    timeopt = int(form.getfirst("timeopt", [1])[0])
    if timeopt == 2:
        year3 = int(form.getfirst("year3"))
        month3 = int(form.getfirst("month3"))
        day3 = int(form.getfirst("day3"))
        hour3 = int(form.getfirst("hour3"))
        minute3 = int(form.getfirst("minute3"))
        sts = utc(year3, month3, day3, hour3, minute3)
        fn = "wwa_%s" % (sts.strftime("%Y%m%d%H%M"),)

    os.chdir("/tmp/")
    for suffix in ["shp", "shx", "dbf", "txt", "zip"]:
        if os.path.isfile("%s.%s" % (fn, suffix)):
            os.remove("%s.%s" % (fn, suffix))

    limiter = ""
    if "limit0" in form:
        limiter += (
            " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' "
        )

    sbwlimiter = " WHERE gtype = 'P' " if "limit1" in form else ""

    warnings_table = "warnings"
    sbw_table = "sbw"
    if sts.year == ets.year:
        warnings_table = "warnings_%s" % (sts.year,)
        sbw_table = "sbw_%s" % (sts.year,)

    geomcol = "geom"
    if form.getfirst("simple", "no") == "yes":
        geomcol = "simple_geom"

    cols = """geo, wfo, utc_issue, utc_expire, utc_prodissue, utc_init_expire,
        phenomena, gtype, significance, eventid,  status, ugc, area2d,
        utc_updated """

    timelimit = "issue >= '%s' and issue < '%s'" % (sts, ets)
    if timeopt == 2:
        timelimit = "issue <= '%s' and issue > '%s' and expire > '%s'" % (
            sts,
            sts + datetime.timedelta(days=-30),
            sts,
        )

    sql = """
    WITH stormbased as (
     SELECT distinct w.geom as geo, 'P'::text as gtype, significance, wfo,
     status, eventid, ''::text as ugc,
     phenomena,
     ST_area( ST_transform(w.geom,2163) ) / 1000000.0 as area2d,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
     to_char(init_expire at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_init_expire,
     to_char(updated at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_updated
     from %(sbw_table)s w %(table_extra)s
     WHERE status = 'NEW' and %(timelimit)s
     %(wfo_limiter)s %(limiter)s
    ),
    countybased as (
     SELECT u.%(geomcol)s as geo, 'C'::text as gtype,
     significance,
     w.wfo, status, eventid, u.ugc, phenomena,
     u.area2163 as area2d,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
     to_char(product_issue at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_prodissue,
     to_char(init_expire at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_init_expire,
     to_char(updated at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_updated
     from %(warnings_table)s w JOIN ugcs u on (u.gid = w.gid) WHERE
     %(timelimit)s %(wfo_limiter2)s %(limiter)s
     )
     SELECT %(cols)s from stormbased UNION ALL
     SELECT %(cols)s from countybased %(sbwlimiter)s
    """ % dict(
        sbw_table=sbw_table,
        timelimit=timelimit,
        wfo_limiter=wfo_limiter,
        limiter=limiter,
        geomcol=geomcol,
        warnings_table=warnings_table,
        table_extra=table_extra,
        wfo_limiter2=wfo_limiter2,
        cols=cols,
        sbwlimiter=sbwlimiter,
    )
    # dump SQL to disk for further debugging
    # o = open('/tmp/daryl.txt', 'w')
    # o.write(sql)
    # o.close()

    cursor = pgconn.cursor(cursor_factory=DictCursor)
    cursor.execute(sql)
    if cursor.rowcount == 0:
        ssw("Content-type: text/plain\n\n")
        ssw("ERROR: No results found for query, please try again")
        sys.exit()

    csv = open("%s.csv" % (fn,), "w")
    csv.write(
        (
            "WFO,ISSUED,EXPIRED,INIT_ISS,INIT_EXP,PHENOM,GTYPE,SIG,ETN,"
            "STATUS,NWS_UGC,AREA_KM2,UPDATED\n"
        )
    )
    with fiona.open(
        "%s.shp" % (fn,),
        "w",
        crs=from_epsg(4326),
        driver="ESRI Shapefile",
        schema={
            "geometry": "MultiPolygon",
            "properties": {
                "WFO": "str:3",
                "ISSUED": "str:12",
                "EXPIRED": "str:12",
                "INIT_ISS": "str:12",
                "INIT_EXP": "str:12",
                "PHENOM": "str:2",
                "GTYPE": "str:1",
                "SIG": "str:1",
                "ETN": "str:4",
                "STATUS": "str:3",
                "NWS_UGC": "str:6",
                "AREA_KM2": "float",
                "UPDATED": "str:12",
            },
        },
    ) as output:
        for row in cursor:
            mp = loads(row["geo"], hex=True)
            csv.write(
                (
                    "%(wfo)s,%(utc_issue)s,%(utc_expire)s,%(utc_prodissue)s,"
                    "%(utc_init_expire)s,%(phenomena)s,%(gtype)s,"
                    "%(significance)s,%(eventid)s,%(status)s,%(ugc)s,"
                    "%(area2d).2f,%(utc_updated)s\n"
                )
                % row
            )
            output.write(
                {
                    "properties": {
                        "WFO": row["wfo"],
                        "ISSUED": row["utc_issue"],
                        "EXPIRED": row["utc_expire"],
                        "INIT_ISS": row["utc_prodissue"],
                        "INIT_EXP": row["utc_init_expire"],
                        "PHENOM": row["phenomena"],
                        "GTYPE": row["gtype"],
                        "SIG": row["significance"],
                        "ETN": row["eventid"],
                        "STATUS": row["status"],
                        "NWS_UGC": row["ugc"],
                        "AREA_KM2": row["area2d"],
                        "UPDATED": row["utc_updated"],
                    },
                    "geometry": mapping(mp),
                }
            )
    csv.close()

    zf = zipfile.ZipFile(fn + ".zip", "w", zipfile.ZIP_DEFLATED)
    zf.write(fn + ".shp")
    zf.write(fn + ".shx")
    zf.write(fn + ".dbf")
    zf.write(fn + ".prj")
    zf.write(fn + ".csv")
    zf.close()

    ssw("Content-type: application/octet-stream\n")
    ssw("Content-Disposition: attachment; filename=%s.zip\n\n" % (fn,))
    ssw(open(fn + ".zip", "rb").read())

    for suffix in ["zip", "shp", "shx", "dbf", "prj", "csv"]:
        os.remove("%s.%s" % (fn, suffix))


if __name__ == "__main__":
    main()
