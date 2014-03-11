#!/usr/bin/env python
''' Produce geojson of ISUSM data '''
import cgi
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import network
import psycopg2
import psycopg2.extras
import datetime
from pyiem.datatypes import temperature
import pytz
import json
ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
cursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)

def drct2txt(val):
    ''' Convert val to textual '''
    if val is None:
        return "N"
    if (val >= 350 or val < 13):
        return "N"
    elif (val >= 13 and val < 35):
        return "NNE"
    elif (val >= 35 and val < 57):
        return "NE"
    elif (val >= 57 and val < 80):
        return "ENE"
    elif (val >= 80 and val < 102):
        return "E"
    elif (val >= 102 and val < 127):
        return "ESE"
    elif (val >= 127 and val < 143):
        return "SE"
    elif (val >= 143 and val < 166):
        return "SSE"
    elif (val >= 166 and val < 190):
        return "S"
    elif (val >= 190 and val < 215):
        return "SSW"
    elif (val >= 215 and val < 237):
        return "SW"
    elif (val >= 237 and val < 260):
        return "WSW"
    elif (val >= 260 and val < 281):
        return "W"
    elif (val >= 281 and val < 304):
        return "WNW"
    elif (val >= 304 and val < 324):
        return "NW"
    elif (val >= 324 and val < 350):
        return "NNW"

def safe_t(val):
    ''' '''
    if val is None:
        return 'M'
    return '%.1f' % (temperature(val, 'C').value('F'),)

def get_data( ts ):
    ''' Get the data for this timestamp '''
    nt = network.Table("ISUSM")
    data = {"type": "FeatureCollection", 
            "crs": {"type": "EPSG", 
                    "properties": {"code": 4326,
                                   "coordinate_order": [1,0]}},
            "features": []}
    cursor.execute("""
    SELECT * from sm_hourly where valid = %s
    """, (ts,))
    for i, row in enumerate(cursor):
        lon = nt.sts[row['station']]['lon']
        lat = nt.sts[row['station']]['lat']
        data['features'].append({"type": "Feature", "id": i,
            "properties": {
                "rh":  "%.0f%%" % (row["rh"],),
                "tmpf": safe_t(row['tair_c_avg']),
                "soil04t": safe_t(row['tsoil_c_avg']),
                "soil12t": safe_t(row['t12_c_avg']),
                "soil24t": safe_t(row['t24_c_avg']),
                "soil50t": safe_t(row['t50_c_avg']),
                "wind": "%s@%.0f" % (drct2txt(row['winddir_d1_wvt']), 
                                    row['ws_mps_s_wvt'] * 2.23)
            },
            "geometry": {"type": "Point",
                        "coordinates": [lon, lat]
            }
        })
    sys.stdout.write(json.dumps(data))

if __name__ == '__main__':
    ''' see how we are called '''
    sys.stdout.write("Content-type: application/json\n\n")
    field = cgi.FieldStorage()
    dt = field.getfirst('dt')
    ts = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.000Z')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    get_data( ts )