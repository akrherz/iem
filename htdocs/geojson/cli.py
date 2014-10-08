#!/usr/bin/env python
""" Produce geojson of CLI data """
import cgi
import sys
import psycopg2.extras
import datetime
import json
import memcache

PGCONN = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = PGCONN.cursor(cursor_factory=psycopg2.extras.DictCursor)

def sanitize(val):
    """ convert to Ms"""
    if val is None:
        return "M"
    return val

def get_data( ts ):
    """ Get the data for this timestamp """
    data = {"type": "FeatureCollection", 
            "crs": {"type": "EPSG", 
                    "properties": {"code": 4326,
                                   "coordinate_order": [1,0]}},
            "features": []}
    # Fetch the daily values
    cursor.execute("""
    select station, name, product, st_x(geom), st_y(geom), 
    high, high_normal, high_record, high_record_years,
    low, low_normal, low_record, low_record_years
    from cli_data c JOIN stations s on (c.station = s.id) 
    WHERE s.network = 'NWSCLI' and c.valid = %s
    """, (ts.date(),))
    for i, row in enumerate(cursor):
        data['features'].append({"type": "Feature", "id": i,
            "properties": {
                "link": "/api/nwstext/%s.txt" % (row['product'],),
                "name": row["name"],
                "high":  str(sanitize(row["high"])),
                "high_record":  str(sanitize(row["high_record"])),
                "high_record_years":  row["high_record_years"],
                "high_normal":  str(sanitize(row["high_normal"])),
                "low":  str(sanitize(row["low"])),
                "low_record":  str(sanitize(row["low_record"])),
                "low_record_years":  row["low_record_years"],
                "low_normal":  str(sanitize(row["low_normal"])),
            },
            "geometry": {"type": "Point",
                        "coordinates": [row['st_x'], row['st_y']]
            }
        })
    return json.dumps(data)

def main():
    ''' see how we are called '''
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")
    field = cgi.FieldStorage()
    dt = field.getfirst('dt', datetime.date.today().strftime("%Y-%m-%d"))
    ts = datetime.datetime.strptime(dt, '%Y-%m-%d')
    cb = field.getfirst('callback', None)

    mckey = "/geojson/cli/%s?callback=%s" % (ts.strftime("%Y%m%d"), cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = get_data(ts)
        mc.set(mckey, res, 300)
    if cb is None:
        sys.stdout.write( res )
    else:
        sys.stdout.write("%s(%s)" % (cb, res))

if __name__ == '__main__':
    main()
