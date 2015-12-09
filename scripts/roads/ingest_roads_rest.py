"""Consume DOT REST Service with Iowa Winter Road Conditions

Run every five minutes from RUN_5MIN.sh
"""
import urllib2
import json
import datetime
import psycopg2

URI = ("http://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
       "Road_Conditions/FeatureServer/0/query?"
       "where=OBJECTID%3E1&outFields=*&returnGeometry=false&f=json")

pgconn = psycopg2.connect(database='postgis', host='iemdb')
cursor = pgconn.cursor()

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
    select c.segid, b.longname, c.cond_code from
    roads_current c JOIN roads_base b on (c.segid = b.segid)
    """)
for row in cursor:
    lookup[row[1]] = row[0]
    current[row[0]] = row[2]

j = json.loads(urllib2.urlopen(URI, timeout=30).read())

for feat in j['features']:
    segid = lookup.get(feat['attributes']['LONGNAME'])
    if segid is None:
        print("ingest_roads_rest unknown longname '%s'" % (
            feat['attributes']['LONGNAME'],))
        continue
    raw = feat['attributes']['HL_PAVEMENT_CONDITION']
    cond = ROADCOND.get(raw)
    if cond is None:
        print(("ingest_roads_reset longname '%s' has unknown cond '%s'"
               ) % (feat['attributes']['LONGNAME'],
                    feat['attributes']['HL_PAVEMENT_CONDITION']))
        continue
    if cond == current[segid]:
        continue
    valid = (datetime.datetime(1970, 1, 1) +
             datetime.timedelta(
                seconds=feat['attributes']['CARS_MSG_UPDATE_DATE']/1000.))
    print valid
    # Save to log
    cursor.execute("""INSERT into roads_2015_2016_log(segid, valid, cond_code,
    raw) VALUES (%s, %s, %s, %s)""", (segid, valid, cond, raw))
    # Update currents
    cursor.execute("""UPDATE roads_current SET cond_code = %s, valid = %s
    WHERE segid = %s""", (cond, valid, segid))

cursor.close()
pgconn.commit()
pgconn.close()
