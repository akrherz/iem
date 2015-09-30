"""Consume a REST service of DOT Snowplow locations and data"""
import urllib2
import json
import psycopg2
import pytz
import datetime

URI = ("https://geonexusr.iowadot.gov/ArcGIS/rest/services/Operations/"
       "Realtime_Trucks/MapServer/1/query?text=&geometry=&"
       "geometryType=esriGeometryPoint&inSR="
       "&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds="
       "&where=label+is+not+null&time=&returnCountOnly=false&"
       "returnIdsOnly=false&returnGeometry=true&maxAllowableOffset="
       "&outSR=&outFields=*&f=json")


def workflow():
    ''' Do stuff '''

    postgis = psycopg2.connect(database='postgis', host='iemdb')
    cursor = postgis.cursor()

    current = {}
    cursor.execute("""SELECT label, valid from idot_snowplow_current""")
    for row in cursor:
        current[row[0]] = row[1]

    valid = datetime.datetime.now()
    valid = valid.replace(tzinfo=pytz.timezone("UTC"), microsecond=0)

    try:
        data = json.loads(urllib2.urlopen(URI, timeout=30).read())
    except Exception, exp:
        # print 'dot_plows download fail %s' % (exp,)
        data = {}
    newplows = {}
    for feat in data.get('features', []):
        logdt = feat['attributes']['LOGDT']
        ts = datetime.datetime.utcfromtimestamp(logdt/1000.)
        valid = valid.replace(year=ts.year, month=ts.month, day=ts.day,
                              hour=ts.hour, minute=ts.minute, second=ts.second)
        label = feat['attributes']['LABEL']

        if current.get(label, None) is None and label not in newplows:
            # print 'New IDOT Snowplow #%s "%s" Valid: %s' % (len(current)+1,
            #                                                label, valid)
            newplows[label] = 1
            cursor.execute("""INSERT into idot_snowplow_current(label, valid)
            VALUES (%s,%s)""", (label, valid))
        if current.get(label, None) is None or current[label] < valid:
            cursor.execute("""
                UPDATE idot_snowplow_current
                SET
                valid = %s,
                heading = %s,
                velocity = %s,
                roadtemp = %s,
                airtemp = %s,
                solidmaterial = %s,
                liquidmaterial = %s,
                prewetmaterial = %s,
                solidsetrate = %s,
                liquidsetrate = %s,
                prewetsetrate = %s,
                leftwingplowstate = %s,
                rightwingplowstate = %s,
                frontplowstate = %s,
                underbellyplowstate = %s,
                solid_spread_code = %s,
                road_temp_code = %s,
                geom = 'SRID=4326;POINT(%s %s)'
                WHERE label = %s
            """, (valid, feat['attributes']['HEADING'],
                  feat['attributes']['VELOCITY'],
                  feat['attributes']['ROADTEMP'],
                  feat['attributes']['AIRTEMP'],
                  feat['attributes']['SOLIDMATERIAL'],
                  feat['attributes']['LIQUIDMATERIAL'],
                  feat['attributes']['PREWETMATERIAL'],
                  feat['attributes']['SOLIDSETRATE'],
                  feat['attributes']['LIQUIDSETRATE'],
                  feat['attributes']['PREWETSETRATE'],
                  feat['attributes']['LEFTWINGPLOWSTATE'],
                  feat['attributes']['RIGHTWINGPLOWSTATE'],
                  feat['attributes']['FRONTPLOWSTATE'],
                  feat['attributes']['UNDERBELLYPLOWSTATE'],
                  feat['attributes']['SOLID_SPREAD_CODE'],
                  feat['attributes']['ROAD_TEMP_CODE'],
                  feat['attributes']['XPOSITION'],
                  feat['attributes']['YPOSITION'],
                  label))
            # Archive it too
            cursor.execute("""
            INSERT into idot_snowplow_2013_2014
            (label, valid, heading, velocity, roadtemp, airtemp, solidmaterial,
            liquidmaterial, prewetmaterial, solidsetrate, liquidsetrate,
            prewetsetrate, leftwingplowstate, rightwingplowstate,
            frontplowstate , underbellyplowstate, solid_spread_code,
            road_temp_code, geom)
             values
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            , %s, 'SRID=4326;POINT(%s %s)')
            """, (label, valid, feat['attributes']['HEADING'],
                  feat['attributes']['VELOCITY'],
                  feat['attributes']['ROADTEMP'],
                  feat['attributes']['AIRTEMP'],
                  feat['attributes']['SOLIDMATERIAL'],
                  feat['attributes']['LIQUIDMATERIAL'],
                  feat['attributes']['PREWETMATERIAL'],
                  feat['attributes']['SOLIDSETRATE'],
                  feat['attributes']['LIQUIDSETRATE'],
                  feat['attributes']['PREWETSETRATE'],
                  feat['attributes']['LEFTWINGPLOWSTATE'],
                  feat['attributes']['RIGHTWINGPLOWSTATE'],
                  feat['attributes']['FRONTPLOWSTATE'],
                  feat['attributes']['UNDERBELLYPLOWSTATE'],
                  feat['attributes']['SOLID_SPREAD_CODE'],
                  feat['attributes']['ROAD_TEMP_CODE'],
                  feat['attributes']['XPOSITION'],
                  feat['attributes']['YPOSITION']))

    postgis.commit()
    postgis.close()

if __name__ == '__main__':
    workflow()
