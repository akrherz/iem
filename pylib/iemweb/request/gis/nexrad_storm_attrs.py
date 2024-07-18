""".. title:: NEXRAD Storm Attributes Data Service

Return to `request form </request/gis/nexrad_storm_attrs.php>`_.

Documentation for /cgi-bin/request/gis/nexrad_storm_attrs.py
------------------------------------------------------------

This service provides IEM processed NWS NEXRAD Storm Attribute table data. This
archive updates in real-time as level 3 NCR products are received.  If you
request more than two radar sites, the time span is limited to 7 days.

Changelog
---------

- 2024-06-11: Initial documentation release

Example Usage
-------------

Provide all attributes between 2024-06-11 00:00 and 2024-06-11 23:59 UTC

https://mesonet.agron.iastate.edu/cgi-bin/request/gis/nexrad_storm_attrs.py?\
fmt=shp&sts=2024-06-11T00:00:00Z&ets=2024-06-11T23:59:59Z

"""

import datetime
import zipfile
from io import BytesIO, StringIO

import shapefile
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    ets: AwareDatetime = Field(None, description="End of Time for request")
    fmt: str = Field(
        "shp", description="Format of output", pattern="^(shp|csv)$"
    )
    radar: ListOrCSVType = Field([], description="Radar Sites to include")
    sts: AwareDatetime = Field(None, description="Start of Time for request")
    year1: int = Field(
        None, description="Year for start of time if sts not set"
    )
    month1: int = Field(
        None, description="Month for start of time if sts not set"
    )
    day1: int = Field(None, description="Day for start of time if sts not set")
    hour1: int = Field(
        None, description="Hour for start of time if sts not set"
    )
    minute1: int = Field(
        None, description="Minute for start of time if sts not set"
    )
    year2: int = Field(None, description="Year for end of time if ets not set")
    month2: int = Field(
        None, description="Month for end of time if ets not set"
    )
    day2: int = Field(None, description="Day for end of time if ets not set")
    hour2: int = Field(None, description="Hour for end of time if ets not set")
    minute2: int = Field(
        None, description="Minute for end of time if ets not set"
    )


def run(environ, start_response):
    """Do something!"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start or end time parameters.")
    sio = StringIO()

    # Need to limit what we are allowing them to request as the file would get
    # massive.  So lets set arbitrary values of
    # 1) If 2 or more RADARs, less than 7 days
    radarlimit = ""
    if environ["radar"] and "ALL" not in environ["radar"]:
        radarlimit = " and nexrad = ANY(:radar) "
    if (
        len(environ["radar"]) > 2
        and (environ["ets"] - environ["sts"]).days > 6
    ):
        environ["ets"] = environ["sts"] + datetime.timedelta(days=7)
    fn = f"stormattr_{environ['sts']:%Y%m%d%H%M}_{environ['ets']:%Y%m%d%H%M}"

    with get_sqlalchemy_conn("radar") as conn:
        res = conn.execute(
            text(f"""
            SELECT to_char(valid at time zone 'UTC', 'YYYYMMDDHH24MI')
                as utctime,
            storm_id, nexrad, azimuth, range, tvs, meso, posh, poh, max_size,
            vil, max_dbz, max_dbz_height, top, drct, sknt,
            ST_y(geom) as lat, ST_x(geom) as lon
            from nexrad_attributes_log WHERE
            valid >= :sts and valid < :ets {radarlimit} ORDER by valid ASC
            """),
            {
                "sts": environ["sts"],
                "ets": environ["ets"],
                "radar": environ["radar"],
            },
        )
        if res.rowcount == 0:
            start_response("200 OK", [("Content-type", "text/plain")])
            return b"ERROR: no results found for your query"

        if environ["fmt"] == "csv":
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
            for row in res:
                sio.write(",".join([str(s) for s in row]) + "\n")
            return sio.getvalue().encode("ascii", "ignore")

        shpio = BytesIO()
        shxio = BytesIO()
        dbfio = BytesIO()

        with shapefile.Writer(shp=shpio, shx=shxio, dbf=dbfio) as shp:
            # C is ASCII characters
            # N is a double precision integer limited to around 18 characters
            #   length
            # D is for dates in the YYYYMMDD format,
            #   with no spaces or hyphens between the sections
            # F is for floating point numbers with the same length limits as N
            # L is for logical data which is stored in the shapefile's attr
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
            for row in res:
                shp.point(row[-1], row[-2])
                shp.record(*row)

    zio = BytesIO()
    with zipfile.ZipFile(
        zio, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        with open("/opt/iem/data/gis/meta/4326.prj", encoding="utf-8") as fh:
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


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Do something fun!"""
    return [run(environ, start_response)]
