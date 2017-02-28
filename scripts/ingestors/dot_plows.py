"""Consume a REST service of DOT Snowplow locations and data"""
import requests
import json
import psycopg2
import pytz
import datetime

URI = ("http://iowadot.maps.arcgis.com/sharing/rest/content/items/"
       "8a3118f14fc24bfb93eb769e997597f9/data")
CEILING = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
CEILING = CEILING.replace(tzinfo=pytz.timezone("UTC"))


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
        req = requests.get(URI, timeout=30)
    except requests.exceptions.ReadTimeout:
        return
    if req.status_code != 200:
        print(("dot_plows got non-200 status_code: %s\n"
               "Content: %s") % (req.status_code, req.content))
        return
    data = json.loads(req.content)
    newplows = {}
    for feat in data['layers'][0].get('featureSet', {}).get('features', []):
        logdt = feat['attributes']['MODIFIEDDT']
        if logdt is None:
            continue
        ts = datetime.datetime.utcfromtimestamp(logdt/1000.)
        valid = valid.replace(year=ts.year, month=ts.month, day=ts.day,
                              hour=ts.hour, minute=ts.minute, second=ts.second)
        if valid > CEILING:
            # print json.dumps(feat, sort_keys=True,
            #                 indent=4, separators=(',', ': '))
            continue
        label = feat['attributes']['LABEL']

        if current.get(label, None) is None and label not in newplows:
            # print 'New IDOT Snowplow #%s "%s" Valid: %s' % (len(current)+1,
            #                                                label, valid)
            newplows[label] = 1
            if len(label) > 20:
                print("Invalid dot_plow feed label of %s" % (repr(label),))
                continue
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
                  None,  # SOIL_SPREAD_CODE
                  None,  # ROAD_TEMP_CODE,
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
                  None,
                  None,
                  feat['attributes']['XPOSITION'],
                  feat['attributes']['YPOSITION']))

    postgis.commit()
    postgis.close()

if __name__ == '__main__':
    workflow()
