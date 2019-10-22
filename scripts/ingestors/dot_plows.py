"""Consume a REST service of DOT Snowplow locations and data."""
import json
import datetime

import requests
from pyiem.util import get_dbconn, utc, exponential_backoff, logger
LOG = logger()

URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "AVL_Direct_View/FeatureServer/0/query?where=1%3D1&objectIds=&time=&"
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
CEILING = utc() + datetime.timedelta(hours=3)


def workflow():
    ''' Do stuff '''
    postgis = get_dbconn('postgis')
    cursor = postgis.cursor()

    current = {}
    cursor.execute("""SELECT label, valid from idot_snowplow_current""")
    for row in cursor:
        current[row[0]] = row[1]

    req = exponential_backoff(requests.get, URI, timeout=30)
    if req is None:
        return
    if req.status_code != 200:
        LOG.info(
            ("dot_plows got non-200 status_code: %s\n"
             "Content: %s"), req.status_code, req.content)
        return
    data = json.loads(req.content)
    for feat in data.get('features', []):
        logdt = feat['attributes']['MODIFIEDDT']
        label = feat['attributes']['LABEL']
        if logdt is None:
            continue
        # Unsure why I do it this way, but alas
        ts = datetime.datetime.utcfromtimestamp(logdt/1000.)
        valid = utc(ts.year, ts.month, ts.day,
                    ts.hour, ts.minute, ts.second)
        if valid > CEILING:
            # print(json.dumps(feat, sort_keys=True,
            #                 indent=4, separators=(',', ': ')))
            continue
        if len(label) > 20:
            LOG.info("Invalid dot_plow feed label of %s", repr(label))
            continue

        if current.get(label) is None:
            # allows subsequent data insert to work
            current[label] = valid - datetime.timedelta(minutes=1)
            cursor.execute("""
                INSERT into idot_snowplow_current(label, valid) VALUES (%s,%s)
            """, (label, valid))
        LOG.debug(
            "logdt: %s label: %s, valid: %s current: %s",
            logdt, label, valid, current[label])
        if current[label] >= valid:
            LOG.debug("    label: %s skipped as old", label)
            continue
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
        """, (
            valid, feat['attributes']['HEADING'],
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
            INSERT into idot_snowplow_""" + str(valid.year) + """
            (label, valid, heading, velocity, roadtemp, airtemp, solidmaterial,
            liquidmaterial, prewetmaterial, solidsetrate, liquidsetrate,
            prewetsetrate, leftwingplowstate, rightwingplowstate,
            frontplowstate , underbellyplowstate, solid_spread_code,
            road_temp_code, geom)
             values
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            , %s, 'SRID=4326;POINT(%s %s)')
        """, (
            label, valid, feat['attributes']['HEADING'],
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
