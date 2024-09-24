""".. title:: Local Storm Report Data Service

Return to `API Services </api/#cgi>`_ or
`User Frontend </request/gis/lsrs.phtml>`_.

Documentation for /cgi-bin/request/gis/lsr.py
---------------------------------------------

This service emits NWS Local Storm Report (LSR) data in various formats. This
dataset is as live as when you query it as reports are ingested in realtime.

Changelog
---------

- 2024-09-23: Added `qualify` as the Estimated, Measured, or Unknown qualifier
  of the magnitude value.  Perhaps fixed a problem with SHP output as well.
- 2024-08-14: Correct bug with reports for Puerto Rico were not included.
- 2024-07-18: Instead of returning a `No results found for query` when no
  database entries are found, we return an empty result.
- 2024-04-05: Initial documentation release and migration to pydantic.
- 2024-04-05: The legacy usage of ``wfo[]`` for CGI arguments is still
  supported, but migration to ``wfo`` is encouraged.

Example Requests
----------------

Provide all Iowa LSRs for 2024 in KML format and then shapefile format.

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py\
?sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&state=IA&fmt=kml

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py\
?sts=2024-01-01T00:00Z&ets=2025-01-01T00:00Z&state=IA&fmt=shp

"""

import datetime
import zipfile
from io import BytesIO, StringIO

import fiona
import geopandas as gpd
import pandas as pd
import shapefile
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

fiona.supported_drivers["KML"] = "rw"
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ISO8660 = "%Y-%m-%dT%H:%M"


class Schema(CGIModel):
    """See how we are called."""

    ets: AwareDatetime = Field(
        None,
        description="The end of the period you are interested in.",
    )
    fmt: str = Field(
        None,
        description="The output format you desire.",
        pattern="^(csv|kml|excel|shp)$",
    )
    justcsv: bool = Field(
        False,
        description="If set, only the CSV file is returned.",
    )
    recent: int = Field(
        None,
        description=(
            "For near realtime requests, the number of seconds to go back in "
            "time.  The timestamp query is the time of the LSR report, not "
            "the time it was disseminated by the NWS. Must be less than "
            "1,000,000 seconds."
        ),
        ge=1,
        le=1_000_000,
    )
    state: ListOrCSVType = Field(
        None,
        description="Limit results to these states.",
    )
    sts: AwareDatetime = Field(
        None,
        description="The start of the period you are interested in.",
    )
    type: ListOrCSVType = Field(
        None,
        description="Limit results to these event types.",
    )
    wfo: ListOrCSVType = Field(
        None,
        description="Limit results to these WFOs.",
    )
    year1: int = Field(
        None,
        description="If sts unset, the start year value in UTC.",
    )
    month1: int = Field(
        None,
        description="If sts unset, the start month value in UTC.",
    )
    day1: int = Field(
        None,
        description="If sts unset, the start day value in UTC.",
    )
    hour1: int = Field(
        0,
        description="If sts unset, the start hour value in UTC.",
    )
    minute1: int = Field(
        0,
        description="If sts unset, the start minute value in UTC.",
    )
    year2: int = Field(
        None,
        description="If ets unset, the end year value in UTC.",
    )
    month2: int = Field(
        None,
        description="If ets unset, the end month value in UTC.",
    )
    day2: int = Field(
        None,
        description="If ets unset, the end day value in UTC.",
    )
    hour2: int = Field(
        0,
        description="If ets unset, the end hour value in UTC.",
    )
    minute2: int = Field(
        0,
        description="If ets unset, the end minute value in UTC.",
    )


def get_time_domain(form):
    """Figure out the start and end timestamps"""
    if form["recent"] is not None:
        # Allow for specifying a recent number of seconds
        ets = utc()
        sts = ets - datetime.timedelta(seconds=form["recent"])
        return sts, ets
    if form["sts"] is None:
        raise IncompleteWebRequest("GET start time parameters missing")
    if form["ets"] is None:
        form["ets"] = utc()
    return form["sts"], form["ets"]


def do_excel_kml(fmt, params, sql_filters):
    """Export as Excel or KML."""
    with get_sqlalchemy_conn("postgis") as conn:
        df: gpd.GeoDataFrame = gpd.read_postgis(
            text(
                f"""
            WITH wfos as (
                select case when length(id) = 4 then substr(id, 2, 3)
                else id end as cwa, tzname from stations where network = 'WFO'
            ), reports as (
                select distinct l.wfo, valid, county, city, l.state, typetext,
                magnitude, l.source, ST_y(l.geom) as lat, ST_x(l.geom) as lon,
                coalesce(remark, '') as remark, u.ugc, u.name as ugcname,
                l.geom, qualifier
                from lsrs l LEFT JOIN ugcs u on (l.gid = u.gid) WHERE
                valid >= :sts and valid < :ets {sql_filters}
            )
            SELECT l.wfo as office,
            to_char(valid at time zone w.tzname,
             'YYYY/MM/DD HH24:MI') as lvalid,
            to_char(valid at time zone 'UTC',
                'YYYY/MM/DD HH24:MI') as utcvalid,
            county, city, state, typetext, magnitude, source, lat, lon,
            remark, ugc, ugcname, geom, qualifier
            from reports l JOIN wfos w on (l.wfo = w.cwa)
            ORDER by utcvalid ASC"""
            ),
            conn,
            params=params,
            geom_col="geom",
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
            "qualifier": "Qualifier",
            "remark": "Remark",
        },
        axis=1,
    )
    if fmt == "excel":
        if len(df.index) >= 1048576:
            raise IncompleteWebRequest("Too many results for Excel export.")
        df = df.drop(columns="geom")
        bio = BytesIO()
        # pylint: disable=abstract-class-instantiated
        writer = pd.ExcelWriter(bio, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Local Storm Reports", index=False)
        worksheet = writer.sheets["Local Storm Reports"]
        worksheet.set_column("B:C", 36)
        worksheet.set_column("D:E", 24)
        worksheet.set_column("G:G", 24)
        worksheet.set_column("I:I", 24)
        worksheet.set_column("L:L", 100)
        worksheet.freeze_panes(1, 0)
        writer.close()
        return bio.getvalue()
    # KML
    df["name"] = df["Location"] + ": " + df["Event Type"]
    fp = BytesIO()
    with fiona.drivers():
        df.to_file(fp, driver="KML", NameField="name", engine="fiona")
    return fp.getvalue()


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go"""
    if environ["REQUEST_METHOD"] == "OPTIONS":
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        return [b"Allow: GET,POST,OPTIONS"]

    params = {}
    params["sts"], params["ets"] = get_time_domain(environ)
    params["states"] = environ["state"]
    params["wfos"] = environ["wfo"]
    params["types"] = environ["type"]

    sql_filters = ""
    if params["states"] and "_ALL" not in params["states"]:
        sql_filters += " and l.state = ANY(:states) "
    if params["wfos"] and "ALL" not in params["wfos"]:
        sql_filters += " and l.wfo = ANY(:wfos) "
    if params["types"] and "ALL" not in params["types"]:
        sql_filters += " and l.typetext = ANY(:types) "

    fn = f"lsr_{params['sts']:%Y%m%d%H%M}_{params['ets']:%Y%m%d%H%M}"
    if environ["fmt"] == "excel":
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}.xlsx"),
        ]
        start_response("200 OK", headers)
        return [do_excel_kml("excel", params, sql_filters)]

    if environ["fmt"] == "kml":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}.kml"),
        ]
        start_response("200 OK", headers)
        return [do_excel_kml("kml", params, sql_filters)]

    csv = StringIO()
    csv.write(
        "VALID,VALID2,LAT,LON,MAG,WFO,TYPECODE,TYPETEXT,CITY,"
        "COUNTY,STATE,SOURCE,REMARK,UGC,UGCNAME,QUALIFIER\n"
    )

    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(
                f"""
            SELECT distinct
            to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI') as dvalid,
            magnitude, l.wfo, type, typetext,
            city, county, l.state, l.source,
            substr(coalesce(remark, ''),0,200) as tremark,
            ST_y(l.geom) as lat, ST_x(l.geom) as lon,
            to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as dvalid2,
            u.ugc, u.name as ugcname, qualifier
            from lsrs l LEFT JOIN ugcs u on (l.gid = u.gid) WHERE
            valid >= :sts and valid < :ets {sql_filters}
            ORDER by dvalid ASC
            """
            ),
            params,
        )

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
            shp.field("UGC", "C", 6)
            shp.field("UGCNAME", "C", 128)
            shp.field("QUALIFY", "C", 1)
            for row in res.mappings():
                tremark = ""
                if row["tremark"] is not None:
                    tremark = (
                        row["tremark"]
                        .encode("utf-8", "ignore")
                        .decode("ascii", "ignore")
                        .replace(",", "_")
                    )
                city = (
                    row["city"]
                    .encode("utf-8", "ignore")
                    .decode("ascii", "ignore")
                )
                record = {
                    "VALID": row["dvalid"],
                    "MAG": row["magnitude"],
                    "WFO": row["wfo"],
                    "TYPECODE": row["type"],
                    "TYPETEXT": row["typetext"],
                    "CITY": row["city"],
                    "COUNTY": row["county"],
                    "STATE": row["state"],
                    "SOURCE": row["source"],
                    "REMARK": tremark,
                    "LAT": row["lat"],
                    "LON": row["lon"],
                    "UGC": row["ugc"],
                    "UGCNAME": row["ugcname"],
                    "QUALIFY": row["qualifier"],
                }
                shp.point(row["lon"], row["lat"])
                shp.record(**record)
                qualify = (
                    row["qualifier"] if row["qualifier"] is not None else ""
                )
                csv.write(
                    f"{row['dvalid']},{row['dvalid2']},{row['lat']:.2f},"
                    f"{row['lon']:.2f},{row['magnitude']},"
                    f"{row['wfo']},{row['type']},{row['typetext']},{city},"
                    f"{row['county']},{row['state']},"
                    f"{row['source']},{tremark},{row['ugc']},{row['ugcname']},"
                    f"{qualify}\n"
                )

    if environ["justcsv"] or environ["fmt"] == "csv":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", f"attachment; filename={fn}.csv"),
        ]
        start_response("200 OK", headers)
        return [csv.getvalue().encode("ascii", "ignore")]

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="utf-8") as fh:
            zf.writestr(f"{fn}.prj", fh.read())
        zf.writestr(f"{fn}.shp", shpio.getvalue())
        zf.writestr(f"{fn}.shx", shxio.getvalue())
        zf.writestr(f"{fn}.dbf", dbfio.getvalue())
        zf.writestr(f"{fn}.csv", csv.getvalue())
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", f"attachment; filename={fn}.zip"),
    ]
    start_response("200 OK", headers)
    return [zio.getvalue()]
