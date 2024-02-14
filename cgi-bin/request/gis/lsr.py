"""Dumps Local Storm Reports on-demand for web requests."""
import datetime
import zipfile
from io import BytesIO, StringIO

import fiona
import geopandas as gpd
import pandas as pd
import shapefile
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import utc
from pyiem.webutil import ensure_list, iemapp
from sqlalchemy import text

fiona.supported_drivers["KML"] = "rw"
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
    if "sts" not in form:
        raise IncompleteWebRequest("GET start time parameters missing")
    if isinstance(form["ets"], str) and form["ets"] == "":
        form["ets"] = utc()
    return form["sts"], form["ets"]


def do_excel_kml(fmt, params, sql_filters):
    """Export as Excel or KML."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            text(
                f"""
            WITH wfos as (
                select case when length(id) = 4 then substr(id, 1, 3)
                else id end as cwa, tzname from stations where network = 'WFO'
            ), reports as (
                select distinct l.wfo, valid, county, city, l.state, typetext,
                magnitude, l.source, ST_y(l.geom) as lat, ST_x(l.geom) as lon,
                coalesce(remark, '') as remark, u.ugc, u.name as ugcname,
                l.geom
                from lsrs l LEFT JOIN ugcs u on (l.gid = u.gid) WHERE
                valid >= :sts and valid < :ets {sql_filters}
            )
            SELECT l.wfo as office,
            to_char(valid at time zone w.tzname,
             'YYYY/MM/DD HH24:MI') as lvalid,
            to_char(valid at time zone 'UTC',
                'YYYY/MM/DD HH24:MI') as utcvalid,
            county, city, state, typetext, magnitude, source, lat, lon,
            remark, ugc, ugcname, geom
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
            "remark": "Remark",
        },
        axis=1,
    )
    if fmt == "excel":
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
        df.to_file(fp, driver="KML", NameField="name")
    return fp.getvalue()


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Go Main Go"""
    if environ["REQUEST_METHOD"] == "OPTIONS":
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        return [b"Allow: GET,POST,OPTIONS"]

    params = {}
    params["sts"], params["ets"] = get_time_domain(environ)

    sql_filters = ""
    for opt in ["state", "states", "states[]"]:
        if opt in environ:
            params["states"] = ensure_list(environ, opt)
            if "_ALL" not in params["states"]:
                sql_filters += " and l.state = ANY(:states) "
    if "wfo[]" in environ:
        params["wfos"] = ensure_list(environ, "wfo[]")
        if "ALL" not in params["wfos"]:
            sql_filters += " and l.wfo = ANY(:wfos) "
    if "type" in environ:
        params["types"] = ensure_list(environ, "type")
        if "ALL" not in params["types"]:
            sql_filters += " and l.typetext = ANY(:types) "

    fn = f"lsr_{params['sts']:%Y%m%d%H%M}_{params['ets']:%Y%m%d%H%M}"
    if environ.get("fmt", "") == "excel":
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}.xlsx"),
        ]
        start_response("200 OK", headers)
        return [do_excel_kml("excel", params, sql_filters)]

    if environ.get("fmt", "") == "kml":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}.kml"),
        ]
        start_response("200 OK", headers)
        return [do_excel_kml("kml", params, sql_filters)]

    csv = StringIO()
    csv.write(
        (
            "VALID,VALID2,LAT,LON,MAG,WFO,TYPECODE,TYPETEXT,CITY,"
            "COUNTY,STATE,SOURCE,REMARK,UGC,UGCNAME\n"
        )
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
            ST_y(l.geom), ST_x(l.geom),
            to_char(valid at time zone 'UTC', 'YYYY/MM/DD HH24:MI') as dvalid2,
            u.ugc, u.name as ugcname
            from lsrs l LEFT JOIN ugcs u on (l.gid = u.gid) WHERE
            valid >= :sts and valid < :ets {sql_filters}
            ORDER by dvalid ASC
            """
            ),
            params,
        )
        if res.rowcount == 0:
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
            shp.field("UGC", "C", 6)
            shp.field("UGCNAME", "C", 128)
            for row in res:
                row = list(row)
                shp.point(row[11], row[10])
                if row[9] is not None:
                    row[9] = (
                        row[9]
                        .encode("utf-8", "ignore")
                        .decode("ascii", "ignore")
                        .replace(",", "_")
                    )
                if row[14] is not None:
                    row[14] = (
                        row[14]
                        .encode("utf-8", "ignore")
                        .decode("ascii", "ignore")
                        .replace(",", "_")
                    )
                shp.record(*row[:-1])
                row5 = (
                    row[5].encode("utf-8", "ignore").decode("ascii", "ignore")
                )
                row9 = row[9] if row[9] is not None else ""
                csv.write(
                    f"{row[0]},{row[12]},{row[10]:.2f},{row[11]:.2f},{row[1]},"
                    f"{row[2]},{row[3]},{row[4]},{row5},{row[6]},{row[7]},"
                    f"{row[8]},{row9},{row[13]},{row[14]}\n"
                )

    if "justcsv" in environ or environ.get("fmt", "") == "csv":
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
