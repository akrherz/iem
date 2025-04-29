""".. title:: NWS Watch/Warning/Advisory (WWA) Data Service

Return to `API Services </api/#cgi>`_ or
`Download User Interface </request/gis/watchwarn.phtml>`_.

Documentation for /cgi-bin/request/gis/watchwarn.py
---------------------------------------------------

This service emits shapefiles (with additional csv included),
or even Excel files.  This service is
rather blunt force and perhaps you should review the mountain of adhoc JSON/API
services found at
`IEM Legacy JSON Services </json/>`_ or at
`IEM API Services </api/1/docs/>`_ .

Changelog
---------

- 2024-10-28: The service default for parameter ``simple`` was set back to
  ``yes``.  It was mistakenly set to ``no`` when this was migrated to pydantic.
- 2024-10-28: Optimize the zipfile response by streaming the result.
- 2024-10-22: Fix and better document the ``at`` parameter for when
  ``timeopt=2``.
- 2024-07-03: Added a `accept=csv` option to allow for CSV output.
- 2024-06-26: Added `limitpds` parameter to limit the request to only include
  products that have a PDS (Particularly Dangerous Situation) tag or phrasing.
- 2024-05-14: To mitigate against large requests that overwhelm the server, a
  limit of one year's worth of data is now in place for requests that do not
  limit the request by either state, phenomena, nor wfo.
- 2024-05-09: Migrated to pydantic based CGI input validation.

Example Usage
-------------

Return all Areal Flood, Flash Flood, Severe Thunderstorm, and Tornado Watch
and Warnings for the state of Mississippi during 2024.  Note how the phenomena
and significance parameters are repeated so that each combination is present.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py?\
accept=shapefile&sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&\
location_group=states&states=MS&limitps=yes&phenomena=FF,FA,SV,TO,FF,FA,SV,TO&\
significance=W,W,W,W,A,A,A,A

Return all Tornado Warnings for the Des Moines WFO in shapefile format during
2023.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py\
?accept=shapefile&sts=2023-01-01T00:00Z&ets=2024-01-01T00:00Z&wfo[]=DMX\
&limitps=yes&phenomena=TO&significance=W

Provide all Tornado Warnings valid at 2120 UTC on 21 May 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py\
?accept=shapefile&at=2024-05-21T21:20Z&timeopt=2&limitps=yes&phenomena=TO\
&significance=W

Same request, but return an excel file

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py\
?accept=excel&at=2024-05-21T21:20Z&timeopt=2&limitps=yes&phenomena=TO\
&significance=W

Same request, but return csv

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py\
?accept=csv&at=2024-05-21T21:20Z&timeopt=2&limitps=yes&phenomena=TO\
&significance=W

Same request, but using the more verbose parameterization for the timestamp

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/watchwarn.py\
?accept=shapefile&year3=2024&month3=5&day3=21&hour3=21&minute3=20&timeopt=2\
&limitps=yes&phenomena=TO&significance=W

"""

import tempfile
import zlib
from datetime import datetime, timedelta
from io import BytesIO
from stat import S_IFREG

import fiona
import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from shapely.geometry import mapping
from shapely.wkb import loads
from stream_zip import ZIP_32, stream_zip

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    accept: str = Field(
        "shapefile",
        pattern="^(shapefile|excel|csv)$",
        description="The format to return, either shapefile or excel.",
    )
    at: AwareDatetime = Field(
        None,
        description=(
            "The timestamp to use when ``timeopt=2``, which the service "
            "provides events valid at the specified time."
        ),
    )
    addsvs: str = Field(
        "no",
        pattern="^(yes|no)$",
        description="Include polygons that were included within any followup "
        "statements after issuance.",
    )
    ets: AwareDatetime = Field(
        None,
        description="The end timestamp in UTC. The format is ISO8601, e.g. "
        "2010-06-01T00:00Z.",
        ge=utc(1986, 1, 1),
    )
    limit0: str = Field(
        "no",
        pattern="^(yes|no)$",
        description="If yes, only include Tornado, Severe Thunderstorm, "
        "Flash Flood, and Marine Warnings.",
    )
    limit1: str = Field(
        "no",
        pattern="^(yes|no)$",
        description="If yes, only include Storm Based Warnings.",
    )
    limit2: str = Field(
        "no",
        pattern="^(yes|no)$",
        description="If yes, only include Emergency Warnings.",
    )
    limitpds: bool = Field(
        False,
        description=(
            "If yes, only include products that have a PDS "
            "(Particularly Dangerous Situation) tag or phrasing."
        ),
    )
    limitps: str = Field(
        "no",
        pattern="^(yes|no)$",
        description="If yes, only include the specified phenomena and "
        "significance.",
    )
    location_group: str = Field(
        "wfo",
        pattern="^(wfo|states)$",
        description="The location group to use, either wfo or states.",
    )
    phenomena: ListOrCSVType = Field(
        ["TO"],
        description="The two character VTEC phenomena(s) to include. If you "
        "provide more than one value, the length must correspond and align "
        "with the ``significance`` parameter.",
    )
    simple: str = Field(
        "yes",
        pattern="^(yes|no)$",
        description="If yes, use a simplified geometry for the UGC "
        "counties/zones.",
    )
    significance: ListOrCSVType = Field(
        ["W"],
        description="The one character VTEC significance to include, if you "
        "provide more than one value, the length must correspond "
        "and align with the ``phenomena`` parameter.",
    )
    states: ListOrCSVType = Field(
        None, description="List of states to include data for."
    )
    sts: AwareDatetime = Field(
        None,
        description="The start timestamp in UTC. The format is ISO8601, e.g. "
        "2010-06-01T00:00Z.",
        ge=utc(1986, 1, 1),
    )
    timeopt: int = Field(
        1,
        description="The time option to use, either 1 or 2, default is 1, "
        "which uses the start and end timestamps to determine "
        "which events to include. Option 2 uses the ``at`` timestamp "
        "to determine which events to include.",
    )
    wfo: ListOrCSVType = Field(
        None, description="List of WFOs to include data for."
    )
    wfos: ListOrCSVType = Field(
        None, description="Legacy parameter, update to use ``wfo``."
    )
    year1: int = Field(
        None,
        description="The start timestamp components in UTC, if you specify a "
        "sts parameter, these are ignored.",
    )
    year2: int = Field(
        None,
        description="The end timestamp components in UTC, if you specify a "
        "ets parameter, these are ignored.",
    )
    year3: int = Field(
        None,
        description=(
            "The ``at`` timestamp components in UTC.  When timeopt is 2, "
            "this is used to find all events that were valid at this "
            "time."
        ),
    )
    month1: int = Field(
        None,
        description="The start timestamp components in UTC, if you specify a "
        "sts parameter, these are ignored.",
    )
    month2: int = Field(
        None,
        description="The end timestamp components in UTC, if you specify a "
        "ets parameter, these are ignored.",
    )
    month3: int = Field(
        None,
        description=(
            "The ``at`` timestamp components in UTC.  When timeopt is 2, "
            "this is used to find all events that were valid at this "
            "time."
        ),
    )
    day1: int = Field(
        None,
        description="The start timestamp components in UTC, if you specify a "
        "sts parameter, these are ignored.",
    )
    day2: int = Field(
        None,
        description="The end timestamp components in UTC, if you specify a "
        "ets parameter, these are ignored.",
    )
    day3: int = Field(
        None,
        description=(
            "The ``at`` timestamp components in UTC.  When timeopt is 2, "
            "this is used to find all events that were valid at this "
            "time."
        ),
    )
    hour1: int = Field(
        None,
        description="The start timestamp components in UTC, if you specify a "
        "sts parameter, these are ignored.",
    )
    hour2: int = Field(
        None,
        description="The end timestamp components in UTC, if you specify a "
        "ets parameter, these are ignored.",
    )
    hour3: int = Field(
        None,
        description=(
            "The ``at`` timestamp components in UTC.  When timeopt is 2, "
            "this is used to find all events that were valid at this "
            "time."
        ),
    )
    minute1: int = Field(
        None,
        description="The start timestamp components in UTC, if you specify a "
        "sts parameter, these are ignored.",
    )
    minute2: int = Field(
        None,
        description="The end timestamp components in UTC, if you specify a "
        "ets parameter, these are ignored.",
    )
    minute3: int = Field(
        None,
        description=(
            "The ``at`` timestamp components in UTC.  When timeopt is 2, "
            "this is used to find all events that were valid at this "
            "time."
        ),
    )


def dfmt(txt):
    """Produce a prettier format for CSV."""
    if txt is None or len(txt) != 12:
        return ""
    return f"{txt[:4]}-{txt[4:6]}-{txt[6:8]} {txt[8:10]}:{txt[10:12]}"


def char3(wfos):
    """Make sure we don't have any 4 char IDs."""
    res = []
    for wfo in wfos:
        res.append(wfo[1:] if len(wfo) == 4 else wfo)  # noqa
    return res


def parse_wfo_location_group(environ, params):
    """Parse wfoLimiter"""
    limiter = ""
    wfos = environ["wfo"]
    if environ["wfos"]:
        wfos = environ["wfos"]
    if wfos is not None and "ALL" not in wfos:
        if len(wfos) == 1:
            wfo = wfos[0]
            wfo = wfo[1:] if len(wfo) == 4 else wfo
            limiter = " and w.wfo = :wfo "
            params["wfo"] = wfo
        else:
            limiter = " and w.wfo = ANY(:wfos) "
            params["wfos"] = char3(wfos)

    return limiter


def build(environ: dict) -> tuple[str, str, dict]:
    """Build the SQL statement."""
    params = {}
    sts = environ["sts"]
    ets = environ["ets"]
    table_extra = ""
    if environ["location_group"] == "states":
        if environ["states"]:
            params["states"] = [x[:2].upper() for x in environ["states"]]
            wfo_limiter = (
                " and ST_Intersects(s.the_geom, w.geom) "
                "and s.state_abbr = ANY(:states) "
            )
            wfo_limiter2 = " and substr(w.ugc, 1, 2) = ANY(:states) "
            table_extra = " , states s "
        else:
            raise IncompleteWebRequest("No state specified")
    else:  # wfo
        wfo_limiter = parse_wfo_location_group(environ, params)
        wfo_limiter2 = wfo_limiter

    if environ["timeopt"] != 2:
        if sts is None or ets is None:
            raise IncompleteWebRequest("Missing start or end time parameters")
        # Keep size low
        if wfo_limiter == "" and (ets - sts) > timedelta(days=366):
            raise IncompleteWebRequest("Please shorten request to <1 year.")
        # Change to postgis db once we have the wfo list
        fn = f"wwa_{sts:%Y%m%d%H%M}_{ets:%Y%m%d%H%M}"
    else:
        if environ["at"] is None:
            year3 = int(environ.get("year3"))
            month3 = int(environ.get("month3"))
            day3 = int(environ.get("day3"))
            hour3 = int(environ.get("hour3"))
            minute3 = int(environ.get("minute3"))
            sts = utc(year3, month3, day3, hour3, minute3)
        else:
            sts = environ["at"]
        ets = sts
        environ["sts"] = sts
        environ["ets"] = ets
        fn = f"wwa_{sts:%Y%m%d%H%M}"

    limiter = ""
    if environ["limit0"] == "yes":
        limiter = (
            " and phenomena IN ('TO','SV','FF','MA') and significance = 'W' "
        )
    if environ["limitps"] == "yes":
        phenom = environ["phenomena"]
        sig = environ["significance"]
        parts = []
        for _i, (p, s) in enumerate(zip(phenom, sig, strict=False)):
            parts.append(f"(phenomena = :p{_i} and significance = :s{_i}) ")
            params[f"p{_i}"] = p[:2]
            params[f"s{_i}"] = s[:1]
        limiter = f" and ({' or '.join(parts)}) "

    sbwlimiter = " WHERE gtype = 'P' " if environ["limit1"] == "yes" else ""

    elimiter = " and is_emergency " if environ["limit2"] == "yes" else ""
    pdslimiter = " and is_pds " if environ["limitpds"] else ""

    warnings_table = "warnings"
    sbw_table = "sbw"
    if sts.year == ets.year:
        warnings_table = f"warnings_{sts.year}"
        sbw_table = f"sbw_{sts.year}"

    geomcol = "geom"
    if environ["simple"] == "yes":
        geomcol = "simple_geom"

    cols = (
        "wfo, utc_issue, utc_expire, utc_prodissue, utc_init_expire, "
        "phenomena, gtype, significance, eventid,  status, ugc, area2d, "
        "utc_updated, hvtec_nwsli, hvtec_severity, hvtec_cause, hvtec_record, "
        "is_emergency, utc_polygon_begin, utc_polygon_end, windtag, hailtag, "
        "tornadotag, damagetag, product_id "
    )
    if environ["accept"] not in ["excel", "csv"]:
        cols = f"geo, {cols}"

    timelimit = f"issue >= '{sts}' and issue < '{ets}'"
    if environ["timeopt"] == 2:
        timelimit = "issue <= :sts and issue > :sts30 and expire > :sts"
        params["sts"] = sts
        params["sts30"] = sts + timedelta(days=-30)
    else:
        if wfo_limiter == "" and limiter == "" and (ets - sts).days > 366:
            raise IncompleteWebRequest(
                "You must limit your request to a year or less."
            )
    sbwtimelimit = timelimit
    statuslimit = " status = 'NEW' "
    if environ["addsvs"] == "yes":
        statuslimit = " status != 'CAN' "
        sbwtimelimit = timelimit.replace(
            "issue",
            "coalesce(issue, polygon_begin)",
        )
    # NB: need distinct since state join could return multiple
    return (
        f"""
    WITH stormbased as (
     SELECT distinct ST_AsBinary(w.geom) as geo, 'P'::text as gtype,
     significance, wfo, status, eventid, ''::text as ugc,
     phenomena,
     ST_area( ST_transform(w.geom,9311) ) / 1000000.0 as area2d,
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
     {wfo_limiter} {limiter} {elimiter} {pdslimiter}
    ),
    countybased as (
     SELECT ST_AsBinary(u.{geomcol}) as geo, 'C'::text as gtype,
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
     {timelimit} {wfo_limiter2} {limiter} {elimiter} {pdslimiter}
     )
     SELECT {cols} from stormbased UNION ALL
     SELECT {cols} from countybased {sbwlimiter}
    """,
        fn,
        params,
    )


def do_excel(sql, fmt, params):
    """Generate an Excel format response."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(sql_helper(sql), conn, params=params, index_col=None)
    if fmt == "excel" and len(df.index) >= 1048576:
        raise IncompleteWebRequest("Result too large for Excel download")
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
    if fmt == "csv":
        return df.to_csv(index=False).encode("ascii")
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="VTEC WaWA", index=False)
    return bio.getvalue()


def process_results_yield_records(cursor, csv):
    """Do something with the results."""
    # Filenames are racy, so we need to have a temp folder
    csv.write(
        "WFO,ISSUED,EXPIRED,INIT_ISS,INIT_EXP,PHENOM,GTYPE,SIG,ETN,"
        "STATUS,NWS_UGC,AREA_KM2,UPDATED,HVTEC_NWSLI,HVTEC_SEVERITY,"
        "HVTEC_CAUSE,HVTEC_RECORD,IS_EMERGENCY,POLYBEGIN,POLYEND,"
        "WINDTAG,HAILTAG,TORNADOTAG,DAMAGETAG,PRODUCT_ID\n"
    )
    for row in cursor.mappings():
        if row["geo"] is None:  # Is this possible?
            continue
        mp = loads(row["geo"])
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
        yield {
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


def local_files(names):
    """Return a generator of local files."""
    now = datetime.now()

    def contents(name: str):
        """Return a generator of file contents."""
        with open(name, "rb") as f:  # skipcq
            while chunk := f.read(65536):
                yield chunk

    return (
        (name.split("/")[-1], now, S_IFREG | 0o644, ZIP_32, contents(name))
        for name in names
    )


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go"""
    try:
        if environ["timeopt"] != 2 and environ["sts"] is None:
            raise IncompleteWebRequest("Missing start time parameter")
        sql, fn, params = build(environ)
    except (IncompleteWebRequest, ValueError) as exp:
        start_response(
            "422 Unprocessable Content", [("Content-type", "text/plain")]
        )
        yield str(exp).encode("ascii")
        return
    if environ["accept"] == "excel":
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}.xlsx"),
        ]
        start_response("200 OK", headers)
        yield do_excel(sql, environ["accept"], params)
        return
    if environ["accept"] == "csv":
        headers = [
            ("Content-type", "text/csv"),
            ("Content-disposition", f"attachment; Filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        yield do_excel(sql, environ["accept"], params)
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        with (
            get_sqlalchemy_conn("postgis") as conn,
            fiona.open(
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
            ) as output,
            open(f"{tmpdir}/{fn}.csv", "w", encoding="ascii") as csv,
            conn.execution_options(
                stream_results=True, max_row_buffer=10000
            ).execute(sql_helper(sql), params) as cursor,
        ):
            output.writerecords(process_results_yield_records(cursor, csv))

        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.zip"),
        ]
        start_response("200 OK", headers)
        zstream = stream_zip(
            local_files(
                (
                    f"{tmpdir}/{fn}.shp",
                    f"{tmpdir}/{fn}.shx",
                    f"{tmpdir}/{fn}.dbf",
                    f"{tmpdir}/{fn}.prj",
                    f"{tmpdir}/{fn}.cpg",
                    f"{tmpdir}/{fn}.csv",
                )
            ),
            get_compressobj=lambda: zlib.compressobj(
                wbits=-zlib.MAX_WBITS, level=1
            ),
        )
        yield from zstream
