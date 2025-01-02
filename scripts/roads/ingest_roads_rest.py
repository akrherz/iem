"""Consume DOT REST Service with Iowa Winter Road Conditions

Run every five minutes from RUN_5MIN.sh

      "attributes" : {
        "OBJECTID" : 38,
        "SEGMENT_ID" : 1883,
        "ROUTE" : "I-35",
        "NAMEID" : "I-35: Swaledale Exit to Exit 194 (Clear Lake)",
        "LONGNAME" : "I-35,.... LAKE)",
        "DISTRICT" : "D2-  Hanlontown-Mason City",
        "SUBAREA" : "Hanlontown",
        "PRIMARYMP" : 182.5526287,
        "PRIMARYLAT" : 42.97979554,
        "PRIMARYLONG" : -93.34460851,
        "SECONDARYMP" : 194.004904,
        "SECONDARYLAT" : 43.145956,
        "SECONDARYLONG" : -93,
        "EVENT_ID" : "IASEG-187400",
        "EVENT_UPDATE" : 73,
        "HL_PAVEMENT_CONDITION" : "seasonal roadway conditions",
        "LOC_LINK_DIRECTION" : "both directions",
        "ROAD_CONDITION" : "Seasonal",
        "GIS_CREATION_DATE" : 1449769515000,
        "CARS_MSG_UPDATE_DATE" : 1449766817000,
        "CARS_MSG_INITIAL_DATE" : 1449766817000,
        "PH_PAVEMENT_CONDITION" : "",
        "SHAPE_Length" : 25598.2073258733
      },

"""

import datetime
import json
import os
import subprocess
import sys
import zipfile

import httpx
import pandas as pd
import shapefile
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.util import exponential_backoff, logger, utc
from shapely.wkb import loads

LOG = logger()
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "511_IA_Road_Conditions_View/FeatureServer/0/query?"
    "where=1%3D1&objectIds=&time=&"
    "geometry=&geometryType=esriGeometryEnvelope&inSR=&"
    "spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&"
    "units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&"
    "returnGeometry=true&multipatchOption=xyFootprint&maxAllowableOffset="
    "&geometryPrecision=&outSR=&datumTransformation=&"
    "applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&"
    "returnCountOnly=false&returnExtentOnly=false&returnDistinctValues=false&"
    "orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&"
    "resultOffset=&resultRecordCount=&returnZ=false&returnM=false&"
    "returnExceededLimitFeatures=true&quantizationParameters=&"
    "sqlFormat=none&f=pjson&token="
)

EPSG26915 = (
    'PROJCS["NAD_1983_UTM_Zone_15N",GEOGCS["GCS_North_American_1983"'
    ',DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,'
    '298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",'
    '0.0174532925199433]],PROJECTION["Transverse_Mercator"],'
    'PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",'
    '0.0],PARAMETER["Central_Meridian",-93.0],PARAMETER'
    '["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0]'
    ',UNIT["Meter",1.0]]'
)
# NB: Could be 'null' (None) as well
ROADCOND = {
    "dry pavement": 0,
    "wet": 1,
    "partially covered with frost": 3,
    "partially covered with snow": 39,
    "partially covered with ice": 27,
    "partially covered with slush": 56,
    "partially covered with mixed": 15,
    "completely covered with frost": 11,
    "completely covered with snow": 47,
    "completely covered with ice": 35,
    "completely covered with slush": 64,
    "completely covered with mixed": 23,
    "travel not advised": 51,
    "partially covered with mixed snow ice or slush": 15,
    "completely covered with mixed snow ice or slush": 23,
    "icy bridges": 27,
    "seasonal": 0,
    "seasonal roadway conditions": 0,
    "impassable": 86,
}


def export_shapefile(txn, valid):
    """Export a Shapefile of Road Conditions"""
    os.chdir("/tmp")
    shp = shapefile.Writer("iaroad_cond")
    shp.field("SEGID", "N", 6, 0)
    shp.field("MAJOR", "S", 10, 0)
    shp.field("MINOR", "S", 128, 0)
    shp.field("US1", "N", 4, 0)
    shp.field("ST1", "N", 4, 0)
    shp.field("INT1", "N", 4, 0)
    shp.field("TYPE", "N", 4, 0)
    shp.field("VALID", "S", 12, 0)
    shp.field("COND_CODE", "N", 4, 0)
    shp.field("COND_TXT", "S", 120, 0)
    shp.field("BAN_TOW", "S", 1, 0)
    shp.field("LIM_VIS", "S", 1, 0)

    txn.execute(
        "select b.*, c.*, b.geom from roads_base b, roads_current c "
        "WHERE b.segid = c.segid and valid is not null and b.geom is not null"
    )
    for row in txn:
        multiline = loads(row["geom"], hex=True)
        shp.line([zip(*multiline.geoms[0].xy)])
        shp.record(
            row["segid"],
            row["major"],
            row["minor"],
            row["us1"],
            row["st1"],
            row["int1"],
            row["type"],
            row["valid"].strftime("%Y%m%d%H%M"),
            row["cond_code"],
            row["raw"],
            str(row["towing_prohibited"])[0],
            str(row["limited_vis"])[0],
        )

    shp.close()
    with open("iaroad_cond.prj", "w", encoding="ascii") as fp:
        fp.write(EPSG26915)
    with zipfile.ZipFile("iaroad_cond.zip", "w") as zfp:
        for suffix in ["shp", "shx", "dbf", "prj"]:
            zfp.write(f"iaroad_cond.{suffix}")

    subprocess.call(
        [
            "pqinsert",
            "-p",
            (
                f"zip ac {valid:%Y%m%d%H%M} "
                "gis/shape/26915/ia/iaroad_cond.zip "
                f"GIS/iaroad_cond_{valid:%Y%m%d%H%M}.zip zip"
            ),
            "iaroad_cond.zip",
        ],
    )

    for suffix in ["shp", "shx", "dbf", "prj", "zip"]:
        os.unlink(f"iaroad_cond.{suffix}")


def main():
    """Go something greatish"""
    pgconn, cursor = get_dbconnc("postgis")

    with get_sqlalchemy_conn("postgis") as conn:
        current = pd.read_sql(
            """
            select c.segid, b.longname, c.cond_code, b.idot_id,
            c.valid at time zone 'UTC' as utc_valid from
            roads_current c JOIN roads_base b on (c.segid = b.segid)
            """,
            conn,
            index_col="idot_id",
        )

    req = exponential_backoff(httpx.get, URI, timeout=30)
    if req is None:
        sys.exit()
    jobj = req.json()

    if "features" not in jobj:
        LOG.warning(
            "Got invalid RESULT:\n%s",
            json.dumps(jobj, sort_keys=True, indent=4, separators=(",", ": ")),
        )
        return

    dirty = False
    for feat in jobj["features"]:
        props = feat["attributes"]
        idot_id = props["SEGMENT_ID"]
        if idot_id not in current.index:
            LOG.warning(
                "Unknown idot_id '%s' with long_name '%s'",
                idot_id,
                props["LONG_NAME"],
            )
            continue
        segid = current.at[idot_id, "segid"]
        raw = props["HL_PAVEMENT_CONDITION"]
        if raw is None:
            continue
        cond = ROADCOND.get(raw.lower())
        if cond is None:
            LOG.warning(
                "longname '%s' has unknown cond '%s'\n%s",
                props["LONG_NAME"],
                props["HL_PAVEMENT_CONDITION"],
                json.dumps(
                    props, sort_keys=True, indent=4, separators=(",", ": ")
                ),
            )
            continue
        # Timestamps appear to be UTC now
        if props["CARS_MSG_UPDATE_DATE"] is not None:
            valid = utc(1970, 1, 1) + datetime.timedelta(
                seconds=props["CARS_MSG_UPDATE_DATE"] / 1000.0
            )
        else:
            # Sucks, but alas
            LOG.info("CARS_MSG_UPDATE_DATE is missing, default to utcnow!")
            valid = utc()
        # Save to log, if difference
        if cond != current.at[idot_id, "cond_code"]:
            cursor.execute(
                """
                INSERT into roads_log(segid, valid, cond_code, raw)
                VALUES (%s, %s, %s, %s)
            """,
                (segid, valid, cond, raw),
            )
            dirty = True
        # Update currents
        cursor.execute(
            "UPDATE roads_current SET cond_code = %s, valid = %s, "
            "raw = %s WHERE segid = %s",
            (cond, valid, raw, segid),
        )

    # Force a run each morning at about 3 AM
    if (
        datetime.datetime.now().hour == 3
        and datetime.datetime.now().minute < 10
    ):
        dirty = True

    if dirty:
        export_shapefile(cursor, datetime.datetime.utcnow())

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
