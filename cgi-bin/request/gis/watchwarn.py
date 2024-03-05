"""Generate a shapefile of warnings based on the CGI request"""

import datetime
import tempfile
import zipfile
from io import BytesIO

import fiona
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import utc
from pyiem.webutil import ensure_list, iemapp
from shapely.geometry import mapping
from shapely.wkb import loads

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def dfmt(text):
    """Produce a prettier format for CSV."""
    if text is None or len(text) != 12:
        return ""
    return f"{text[:4]}-{text[4:6]}-{text[6:8]} {text[8:10]}:{text[10:12]}"


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
        wfos = ensure_list(form, "wfo[]")
        wfos.append("XXX")  # Hack to make next section work
        if "ALL" not in wfos:
            limiter = f" and w.wfo in {tuple(char3(wfos))} "

    if "wfos[]" in form:
        wfos = ensure_list(form, "wfos[]")
        wfos.append("XXX")  # Hack to make next section work
        if "ALL" not in wfos:
            limiter = f" and w.wfo in {tuple(char3(wfos))} "
    return limiter


def build_sql(environ):
    """Build the SQL statement."""
    sts = environ["sts"]
    ets = environ["ets"]
    table_extra = ""
    location_group = environ.get("location_group", "wfo")
    if location_group == "states":
        if "states[]" in environ:
            arstates = ensure_list(environ, "states[]")
            states = [x[:2].upper() for x in arstates]
            states.append("XX")  # Hack for 1 length
            wfo_limiter = (
                " and ST_Intersects(s.the_geom, w.geom) "
                f"and s.state_abbr in {tuple(states)} "
            )
            wfo_limiter2 = f" and substr(w.ugc, 1, 2) in {tuple(states)} "
            table_extra = " , states s "
        else:
            raise ValueError("No state specified")
    elif location_group == "wfo":
        wfo_limiter = parse_wfo_location_group(environ)
        wfo_limiter2 = wfo_limiter
    else:
        # Unknown location_group
        raise ValueError(f"Unknown location_group ({location_group})")

    # Keep size low
    if wfo_limiter == "" and (ets - sts) > datetime.timedelta(days=5 * 365.25):
        raise ValueError("Please shorten request to less than 5 years.")

    # Change to postgis db once we have the wfo list
    fn = f"wwa_{sts:%Y%m%d%H%M}_{ets:%Y%m%d%H%M}"
    timeopt = int(environ.get("timeopt", [1])[0])
    if timeopt == 2:
        year3 = int(environ.get("year3"))
        month3 = int(environ.get("month3"))
        day3 = int(environ.get("day3"))
        hour3 = int(environ.get("hour3"))
        minute3 = int(environ.get("minute3"))
        sts = utc(year3, month3, day3, hour3, minute3)
        fn = f"wwa_{sts:%Y%m%d%H%M}"

    limiter = ""
    if "limit0" in environ:
        limiter = (
            " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' "
        )
    if environ.get("limitps", "no") == "yes":
        phenom = environ.get("phenomena", "TO")[:2]
        sig = environ.get("significance", "W")[:1]
        limiter = f" and phenomena = '{phenom}' and significance = '{sig}' "

    sbwlimiter = " WHERE gtype = 'P' " if "limit1" in environ else ""

    elimiter = " and is_emergency " if "limit2" in environ else ""

    warnings_table = "warnings"
    sbw_table = "sbw"
    if sts.year == ets.year:
        warnings_table = f"warnings_{sts.year}"
        sbw_table = f"sbw_{sts.year}"

    geomcol = "geom"
    if environ.get("simple", "no") == "yes":
        geomcol = "simple_geom"

    cols = (
        "wfo, utc_issue, utc_expire, utc_prodissue, utc_init_expire, "
        "phenomena, gtype, significance, eventid,  status, ugc, area2d, "
        "utc_updated, hvtec_nwsli, hvtec_severity, hvtec_cause, hvtec_record, "
        "is_emergency, utc_polygon_begin, utc_polygon_end, windtag, hailtag, "
        "tornadotag, damagetag, product_id "
    )
    if environ.get("accept") != "excel":
        cols = f"geo, {cols}"

    timelimit = f"issue >= '{sts}' and issue < '{ets}'"
    if timeopt == 2:
        timelimit = (
            f"issue <= '{sts}' and "
            f"issue > '{sts + datetime.timedelta(days=-30)}' and "
            f"expire > '{sts}'"
        )
    sbwtimelimit = timelimit
    statuslimit = " status = 'NEW' "
    if environ.get("addsvs", "no") == "yes":
        statuslimit = " status != 'CAN' "
        sbwtimelimit = timelimit.replace(
            "issue",
            "coalesce(issue, polygon_begin)",
        )
    # NB: need distinct since state join could return multiple
    return (
        f"""
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
     windtag, hailtag, tornadotag,
     coalesce(damagetag, floodtag_damage) as damagetag,
     product_id
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
     null::varchar as damagetag,
     product_ids[1] as product_id
     from {warnings_table} w JOIN ugcs u on (u.gid = w.gid) WHERE
     {timelimit} {wfo_limiter2} {limiter} {elimiter}
     )
     SELECT {cols} from stormbased UNION ALL
     SELECT {cols} from countybased {sbwlimiter}
    """,
        fn,
    )


def do_excel(sql):
    """Generate an Excel format response."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(sql, conn, index_col=None)
    # Back-convert datetimes :/
    for col in (
        "utc_issue utc_expire utc_prodissue utc_updated utc_polygon_begin "
        "utc_polygon_end"
    ).split():
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce",
            format="%Y%m%d%H%M",
        ).dt.strftime("%Y-%m-%d %H:%M")
    bio = BytesIO()
    # pylint: disable=abstract-class-instantiated
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="VTEC WaWA", index=False)
    return bio.getvalue()


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Go Main Go"""
    if "sts" not in environ:
        raise IncompleteWebRequest("Missing start time parameters")
    try:
        sql, fn = build_sql(environ)
    except ValueError as exp:
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        return [str(exp).encode("ascii")]

    accept = environ.get("accept", "shapefile")
    if accept == "excel":
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}.xlsx"),
        ]
        start_response("200 OK", headers)
        return [do_excel(sql)]
    pgconn, cursor = get_dbconnc("postgis")
    cursor.close()  # lazy
    cursor = pgconn.cursor("streaming")

    cursor.execute(sql)
    # TODO if cursor.rowcount == 0:
    #    start_response("200 OK", [("Content-type", "text/plain")])
    #    return [b"ERROR: No results found for query, please try again"]

    # Filenames are racy, so we need to have a temp folder
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/{fn}.csv", "w", encoding="ascii") as csv:
            csv.write(
                "WFO,ISSUED,EXPIRED,INIT_ISS,INIT_EXP,PHENOM,GTYPE,SIG,ETN,"
                "STATUS,NWS_UGC,AREA_KM2,UPDATED,HVTEC_NWSLI,HVTEC_SEVERITY,"
                "HVTEC_CAUSE,HVTEC_RECORD,IS_EMERGENCY,POLYBEGIN,POLYEND,"
                "WINDTAG,HAILTAG,TORNADOTAG,DAMAGETAG,PRODUCT_ID\n"
            )
            with fiona.open(
                f"{tmpdir}/{fn}.shp",
                "w",
                crs="EPSG:4326",
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
                        "PROD_ID": "str:36",
                    },
                },
            ) as output:
                for row in cursor:
                    if row["geo"] is None:
                        continue
                    mp = loads(row["geo"], hex=True)
                    csv.write(
                        f"{row['wfo']},{dfmt(row['utc_issue'])},"
                        f"{dfmt(row['utc_expire'])},"
                        f"{dfmt(row['utc_prodissue'])},"
                        f"{dfmt(row['utc_init_expire'])},"
                        f"{row['phenomena']},{row['gtype']},"
                        f"{row['significance']},{row['eventid']},"
                        f"{row['status']},"
                        f"{row['ugc']},{row['area2d']:.2f},"
                        f"{dfmt(row['utc_updated'])},"
                        f"{row['hvtec_nwsli']},{row['hvtec_severity']},"
                        f"{row['hvtec_cause']},{row['hvtec_record']},"
                        f"{row['is_emergency']},"
                        f"{dfmt(row['utc_polygon_begin'])},"
                        f"{dfmt(row['utc_polygon_end'])},{row['windtag']},"
                        f"{row['hailtag']},{row['tornadotag']},"
                        f"{row['damagetag']},{row['product_id']}\n"
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
                                "PROD_ID": row["product_id"],
                            },
                            "geometry": mapping(mp),
                        }
                    )

        with zipfile.ZipFile(
            f"{tmpdir}/{fn}.zip", "w", zipfile.ZIP_DEFLATED
        ) as zf:
            for suffix in ["shp", "shx", "dbf", "cpg", "prj", "csv"]:
                zf.write(f"{tmpdir}/{fn}.{suffix}", f"{fn}.{suffix}")
        with open(f"{tmpdir}/{fn}.zip", "rb") as fh:
            payload = fh.read()
    pgconn.close()
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)

    return [payload]
