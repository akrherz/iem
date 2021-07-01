"""Generate a shapefile of warnings based on the CGI request"""
import zipfile
import os
import datetime

from psycopg2.extras import DictCursor
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping
from shapely.wkb import loads
from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc


def df(text):
    """Produce a prettier format for CSV."""
    if text is None or len(text) != 12:
        return ""
    return f"{text[:4]}-{text[4:6]}-{text[6:8]} {text[8:10]}:{text[10:12]}"


def get_time_extent(form):
    """Figure out the time extent of this request"""
    if "year" in form:
        year1 = form.get("year")
        year2 = form.get("year")
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
        wfos = form.getall("wfo[]")
        wfos.append("XXX")  # Hack to make next section work
        if "ALL" not in wfos:
            limiter = " and w.wfo in %s " % (str(tuple(char3(wfos))),)

    if "wfos[]" in form:
        wfos = form.getall("wfos[]")
        wfos.append("XXX")  # Hack to make next section work
        if "ALL" not in wfos:
            limiter = " and w.wfo in %s " % (str(tuple(char3(wfos))),)
    return limiter


def application(environ, start_response):
    """Go Main Go"""
    form = parse_formvars(environ)
    try:
        sts, ets = get_time_extent(form)
    except ValueError:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [
            b"An invalid date was specified, please check that the day of the "
            b"month exists for your selection (ie June 31st vs June 30th)."
        ]

    table_extra = ""
    location_group = form.get("location_group", "wfo")
    if location_group == "states":
        if "states[]" in form:
            states = [x[:2].upper() for x in form.getall("states[]")]
            states.append("XX")  # Hack for 1 length
            wfo_limiter = (
                " and ST_Intersects(s.the_geom, w.geom) "
                "and s.state_abbr in %s "
            ) % (tuple(states),)
            wfo_limiter2 = (" and substr(w.ugc, 1, 2) in %s ") % (
                str(tuple(states)),
            )
            table_extra = " , states s "
        else:
            start_response("200 OK", [("Content-type", "text/plain")])
            return [b"No state specified"]
    elif location_group == "wfo":
        wfo_limiter = parse_wfo_location_group(form)
        wfo_limiter2 = wfo_limiter
    else:
        # Unknown location_group
        msg = "Unknown location_group (%s)" % (location_group,)
        start_response("200 OK", [("Content-type", "text/plain")])
        return [msg.encode("ascii")]

    # Keep size low
    if wfo_limiter == "" and (ets - sts) > datetime.timedelta(days=5 * 365.25):
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Please shorten request to less than 5 years."]

    # Change to postgis db once we have the wfo list
    pgconn = get_dbconn("postgis", user="nobody")
    fn = "wwa_%s_%s" % (sts.strftime("%Y%m%d%H%M"), ets.strftime("%Y%m%d%H%M"))
    timeopt = int(form.get("timeopt", [1])[0])
    if timeopt == 2:
        year3 = int(form.get("year3"))
        month3 = int(form.get("month3"))
        day3 = int(form.get("day3"))
        hour3 = int(form.get("hour3"))
        minute3 = int(form.get("minute3"))
        sts = utc(year3, month3, day3, hour3, minute3)
        fn = "wwa_%s" % (sts.strftime("%Y%m%d%H%M"),)

    os.chdir("/tmp/")
    for suffix in ["shp", "shx", "dbf", "txt", "zip"]:
        if os.path.isfile("%s.%s" % (fn, suffix)):
            os.remove("%s.%s" % (fn, suffix))

    limiter = ""
    if "limit0" in form:
        limiter = (
            " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' "
        )
    if form.get("limitps", "no") == "yes":
        phenom = form.get("phenomena", "TO")[:2]
        sig = form.get("significance", "W")[:1]
        limiter = f" and phenomena = '{phenom}' and significance = '{sig}' "

    sbwlimiter = " WHERE gtype = 'P' " if "limit1" in form else ""

    elimiter = " and is_emergency " if "limit2" in form else ""

    warnings_table = "warnings"
    sbw_table = "sbw"
    if sts.year == ets.year:
        warnings_table = "warnings_%s" % (sts.year,)
        sbw_table = "sbw_%s" % (sts.year,)

    geomcol = "geom"
    if form.get("simple", "no") == "yes":
        geomcol = "simple_geom"

    cols = """geo, wfo, utc_issue, utc_expire, utc_prodissue, utc_init_expire,
        phenomena, gtype, significance, eventid,  status, ugc, area2d,
        utc_updated, hvtec_nwsli, hvtec_severity, hvtec_cause, hvtec_record,
        is_emergency, utc_polygon_begin, utc_polygon_end, windtag, hailtag,
        tornadotag, damagetag """

    timelimit = "issue >= '%s' and issue < '%s'" % (sts, ets)
    if timeopt == 2:
        timelimit = "issue <= '%s' and issue > '%s' and expire > '%s'" % (
            sts,
            sts + datetime.timedelta(days=-30),
            sts,
        )
    sbwtimelimit = timelimit
    statuslimit = " status = 'NEW' "
    if form.get("addsvs", "no") == "yes":
        statuslimit = " status != 'CAN' "
        sbwtimelimit = timelimit.replace(
            "issue",
            "coalesce(issue, polygon_begin)",
        )
    # NB: need distinct since state join could return multiple
    sql = f"""
    WITH stormbased as (
     SELECT distinct w.geom as geo, 'P'::text as gtype, significance, wfo,
     status, eventid, ''::text as ugc,
     phenomena,
     ST_area( ST_transform(w.geom,2163) ) / 1000000.0 as area2d,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_prodissue,
     to_char(polygon_begin at time zone 'UTC', 'YYYYMMDDHH24MI')
        as utc_polygon_begin,
     to_char(polygon_end at time zone 'UTC', 'YYYYMMDDHH24MI')
        as utc_polygon_end,
     to_char(init_expire at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_init_expire,
     to_char(updated at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_updated,
     hvtec_nwsli, hvtec_severity, hvtec_cause, hvtec_record, is_emergency,
     windtag, hailtag, tornadotag, damagetag
     from {sbw_table} w {table_extra}
     WHERE {statuslimit} and {sbwtimelimit}
     {wfo_limiter} {limiter} {elimiter}
    ),
    countybased as (
     SELECT u.{geomcol} as geo, 'C'::text as gtype,
     significance,
     w.wfo, status, eventid, u.ugc, phenomena,
     u.area2163 as area2d,
     to_char(expire at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_expire,
     to_char(issue at time zone 'UTC', 'YYYYMMDDHH24MI') as utc_issue,
     to_char(product_issue at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_prodissue,
     null as utc_polygon_begin,
     null as utc_polygon_end,
     to_char(init_expire at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_init_expire,
     to_char(updated at time zone 'UTC',
             'YYYYMMDDHH24MI') as utc_updated,
     hvtec_nwsli, hvtec_severity, hvtec_cause, hvtec_record, is_emergency,
     null::real as windtag, null::real as hailtag, null::varchar as tornadotag,
     null::varchar as damagetag
     from {warnings_table} w JOIN ugcs u on (u.gid = w.gid) WHERE
     {timelimit} {wfo_limiter2} {limiter} {elimiter}
     )
     SELECT {cols} from stormbased UNION ALL
     SELECT {cols} from countybased {sbwlimiter}
    """
    print(sql)
    cursor = pgconn.cursor(cursor_factory=DictCursor)
    cursor.execute(sql)
    if cursor.rowcount == 0:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: No results found for query, please try again"]

    csv = open("%s.csv" % (fn,), "w")
    csv.write(
        (
            "WFO,ISSUED,EXPIRED,INIT_ISS,INIT_EXP,PHENOM,GTYPE,SIG,ETN,"
            "STATUS,NWS_UGC,AREA_KM2,UPDATED,HVTEC_NWSLI,HVTEC_SEVERITY,"
            "HVTEC_CAUSE,HVTEC_RECORD,IS_EMERGENCY,POLYBEGIN,POLYEND,WINDTAG,"
            "HAILTAG,TORNADOTAG,DAMAGETAG\n"
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
                "HV_NWSLI": "str:5",
                "HV_SEV": "str:1",
                "HV_CAUSE": "str:2",
                "HV_REC": "str:2",
                "EMERGENC": "bool",
                "POLY_BEG": "str:12",
                "POLY_END": "str:12",
                "WINDTAG": "float",
                "HAILTAG": "float",
                "TORNTAG": "str:16",
                "DAMAGTAG": "str:16",
            },
        },
    ) as output:
        for row in cursor:
            mp = loads(row["geo"], hex=True)
            csv.write(
                f"{row['wfo']},{df(row['utc_issue'])},{df(row['utc_expire'])},"
                f"{df(row['utc_prodissue'])},{df(row['utc_init_expire'])},"
                f"{row['phenomena']},{row['gtype']},"
                f"{row['significance']},{row['eventid']},{row['status']},"
                f"{row['ugc']},{row['area2d']:.2f},{df(row['utc_updated'])},"
                f"{row['hvtec_nwsli']},{row['hvtec_severity']},"
                f"{row['hvtec_cause']},{row['hvtec_record']},"
                f"{row['is_emergency']},{df(row['utc_polygon_begin'])},"
                f"{df(row['utc_polygon_end'])},{row['windtag']},"
                f"{row['hailtag']},{row['tornadotag']},{row['damagetag']}\n"
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
                        "HV_NWSLI": row["hvtec_nwsli"],
                        "HV_SEV": row["hvtec_severity"],
                        "HV_CAUSE": row["hvtec_cause"],
                        "HV_REC": row["hvtec_record"],
                        "EMERGENC": row["is_emergency"],
                        "POLY_BEG": row["utc_polygon_begin"],
                        "POLY_END": row["utc_polygon_end"],
                        "WINDTAG": row["windtag"],
                        "HAILTAG": row["hailtag"],
                        "TORNTAG": row["tornadotag"],
                        "DAMAGTAG": row["damagetag"],
                    },
                    "geometry": mapping(mp),
                }
            )
    csv.close()

    with zipfile.ZipFile(fn + ".zip", "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(fn + ".shp")
        zf.write(fn + ".shx")
        zf.write(fn + ".dbf")
        zf.write(fn + ".cpg")
        zf.write(fn + ".prj")
        zf.write(fn + ".csv")

    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=%s.zip" % (fn,)),
    ]
    start_response("200 OK", headers)
    payload = open(fn + ".zip", "rb").read()

    for suffix in ["zip", "shp", "shx", "dbf", "prj", "csv", "cpg"]:
        fullfn = f"{fn}.{suffix}"
        if os.path.isfile(fullfn):
            os.remove(fullfn)

    return [payload]
