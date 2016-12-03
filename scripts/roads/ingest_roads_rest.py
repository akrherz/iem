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
import json
import datetime
import sys
import psycopg2.extras
import shapelib
import requests
import dbflib
from pyiem.util import exponential_backoff
from pyiem import wellknowntext
import zipfile
import subprocess
import os

EPSG26915 = ('PROJCS["NAD_1983_UTM_Zone_15N",GEOGCS["GCS_North_American_1983"'
             ',DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,'
             '298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",'
             '0.0174532925199433]],PROJECTION["Transverse_Mercator"],'
             'PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",'
             '0.0],PARAMETER["Central_Meridian",-93.0],PARAMETER'
             '["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0]'
             ',UNIT["Meter",1.0]]')


def export_shapefile(txn, tp):
    """Export a Shapefile of Road Conditions"""
    os.chdir("/tmp")
    dbf = dbflib.create("iaroad_cond")
    dbf.add_field("SEGID", dbflib.FTInteger, 6, 0)
    dbf.add_field("MAJOR", dbflib.FTString, 10, 0)
    dbf.add_field("MINOR", dbflib.FTString, 128, 0)
    dbf.add_field("US1", dbflib.FTInteger, 4, 0)
    dbf.add_field("ST1", dbflib.FTInteger, 4, 0)
    dbf.add_field("INT1", dbflib.FTInteger, 4, 0)
    dbf.add_field("TYPE", dbflib.FTInteger, 4, 0)
    dbf.add_field("VALID", dbflib.FTString, 12, 0)
    dbf.add_field("COND_CODE", dbflib.FTInteger, 4, 0)
    dbf.add_field("COND_TXT", dbflib.FTString, 120, 0)
    dbf.add_field("BAN_TOW", dbflib.FTString, 1, 0)
    dbf.add_field("LIM_VIS", dbflib.FTString, 1, 0)

    shp = shapelib.create("iaroad_cond", shapelib.SHPT_ARC)

    txn.execute("""select b.*, c.*, ST_astext(b.geom) as bgeom from
         roads_base b, roads_current c WHERE b.segid = c.segid
         and valid is not null and b.geom is not null""")
    i = 0
    for row in txn:
        s = row["bgeom"]
        f = wellknowntext.convert_well_known_text(s)
        valid = row["valid"]
        d = {}
        d["SEGID"] = row["segid"]
        d["MAJOR"] = row["major"]
        d["MINOR"] = row["minor"]
        d["US1"] = row["us1"]
        d["ST1"] = row["st1"]
        d["INT1"] = row["int1"]
        d["TYPE"] = row["type"]
        d["VALID"] = valid.strftime("%Y%m%d%H%M")
        d["COND_CODE"] = row["cond_code"]
        d["COND_TXT"] = row["raw"]
        d["BAN_TOW"] = str(row["towing_prohibited"])[0]
        d["LIM_VIS"] = str(row["limited_vis"])[0]

        obj = shapelib.SHPObject(shapelib.SHPT_ARC, 1, f)
        shp.write_object(-1, obj)
        dbf.write_record(i, d)

        del(obj)
        i += 1

    del(shp)
    del(dbf)
    z = zipfile.ZipFile("iaroad_cond.zip", 'w')
    z.write("iaroad_cond.shp")
    z.write("iaroad_cond.shx")
    z.write("iaroad_cond.dbf")
    o = open('iaroad_cond.prj', 'w')
    o.write(EPSG26915)
    o.close()
    z.write("iaroad_cond.prj")
    z.close()

    utc = tp + datetime.timedelta(hours=6)
    subprocess.call(("/home/ldm/bin/pqinsert -p 'zip ac %s "
                     "gis/shape/26915/ia/iaroad_cond.zip "
                     "GIS/iaroad_cond_%s.zip zip' iaroad_cond.zip"
                     "") % (utc.strftime("%Y%m%d%H%M"),
                            utc.strftime("%Y%m%d%H%M")), shell=True)

    for suffix in ['shp', 'shx', 'dbf', 'prj', 'zip']:
        os.unlink("iaroad_cond.%s" % (suffix,))

URI = ("http://iowadot.maps.arcgis.com/sharing/rest/content/items/"
       "5d6c7d6963e549539ead6e50d89bdd08/data")

pgconn = psycopg2.connect(database='postgis', host='iemdb')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# NB: Could be 'null' (None) as well
ROADCOND = {
    'dry pavement': 0,
    'wet': 1,
    'partially covered with frost': 3,
    'partially covered with snow': 39,
    'partially covered with ice': 27,
    'partially covered with slush': 56,
    'partially covered with mix': 15,
    'completely covered with frost': 11,
    'completely covered with snow': 47,
    'completely covered with ice': 35,
    'completely covered with slush': 64,
    'completely covered with mixed': 23,
    'travel not advised': 51,
    'impassable': 86,
    'partially covered with mixed snow ice or slush': 15,
    'completely covered with mixed snow ice or slush': 23,
    'icy bridges': 27,
    'seasonal': 0,
    'Seasonal': 0,
    'seasonal roadway conditions': 0,
    'impassable': 86,
            }

lookup = {}
current = {}
cursor.execute("""
    select c.segid, b.longname, c.cond_code, b.idot_id from
    roads_current c JOIN roads_base b on (c.segid = b.segid)
    """)
for row in cursor:
    lookup[row[3]] = row[0]
    current[row[0]] = row[2]

r = exponential_backoff(requests.get, URI, timeout=30)
if r is None:
    sys.exit()
j = r.json()

if 'layers' not in j:
    print(('ingest_roads_rest got invalid RESULT:\n%s' % (
                json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')
                           ))))
    sys.exit()

featureset = j['layers'][0]['featureSet']
dirty = False
for feat in featureset['features']:
    props = feat['attributes']
    segid = lookup.get(props['SEGMENT_ID'])
    if segid is None:
        print("ingest_roads_rest unknown longname '%s' segment_id '%s'" % (
            props['LONGNAME'], props['SEGMENT_ID']))
        continue
    raw = props['HL_PAVEMENT_CONDITION']
    if raw is None:
        continue
    cond = ROADCOND.get(raw)
    if cond is None:
        print(("ingest_roads_reset longname '%s' has unknown cond '%s'\n%s"
               ) % (props['LONGNAME'],
                    props['HL_PAVEMENT_CONDITION'],
                    json.dumps(props, sort_keys=True,
                               indent=4, separators=(',', ': '))))
        continue
    if cond == current[segid]:
        continue
    # Timestamps appear to be UTC now
    valid = datetime.datetime(1970, 1, 1) + datetime.timedelta(
        seconds=props['CARS_MSG_UPDATE_DATE']/1000.)
    print valid
    # Save to log
    cursor.execute("""INSERT into roads_2015_2016_log(segid, valid, cond_code,
    raw) VALUES (%s, %s, %s, %s)""", (segid,
                                      valid.strftime("%Y-%m-%d %H:%M"),
                                      cond, raw))
    # Update currents
    cursor.execute("""UPDATE roads_current SET cond_code = %s, valid = %s,
    raw = %s WHERE segid = %s
    """, (cond, valid.strftime("%Y-%m-%d %H:%M"), raw, segid))
    dirty = True

if dirty:
    export_shapefile(cursor, valid)

cursor.close()
pgconn.commit()
pgconn.close()
