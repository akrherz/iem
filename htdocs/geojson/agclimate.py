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

def get_data( ts, varname ):
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
        if varname == 'rh':
            value = "%.0f%%" % (row["rh"],)
        elif varname == 'tmpf':
            value = "%.1f" % (temperature(row['tair_c_avg'], 'C').value('F'))
        elif varname == 'wind':
            value = "%s@%.0f" % (row['winddir_d1_wvt'], 
                                 row['ws_mps_s_wvt'] * 2.23)
        lon = nt.sts[row['station']]['lon']
        lat = nt.sts[row['station']]['lat']
        data['features'].append({"type": "Feature", "id": i,
                                 "properties": {"value": value
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
    varname = field.getfirst('varname', 'rh')
    get_data( ts, varname )