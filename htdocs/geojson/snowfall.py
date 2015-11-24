#!/usr/bin/env python
""" Produce geojson of Snowfall data """
import cgi
import sys
import psycopg2.extras
import datetime
import json
import memcache
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

PGCONN = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = PGCONN.cursor(cursor_factory=psycopg2.extras.DictCursor)


def sanitize(val):
    """ convert to Ms"""
    if val is None:
        return "M"
    if val == 0.0001:
        return "T"
    return val


def get_data(ts):
    """ Get the data for this timestamp """
    data = {"type": "FeatureCollection",
            "crs": {"type": "EPSG",
                    "properties": {"code": 4326,
                                   "coordinate_order": [1, 0]}},
            "features": []}
    # Fetch the daily values
    cursor.execute("""
    select id as station, name, state, wfo,
    round(st_x(geom)::numeric, 4)::float as st_x,
    round(st_y(geom)::numeric, 4)::float as st_y,
    snow
    from summary s JOIN stations t on (s.iemid = t.iemid)
    WHERE s.day = %s and s.snow >= 0 and t.network = 'IA_COOP' LIMIT 5
    """, (ts.date(),))
    for i, row in enumerate(cursor):
        data['features'].append({"type": "Feature", "id": i, "properties": {
                "station": row["station"],
                "state": row["state"],
                "wfo": row["wfo"],
                "name": row["name"],
                "snow":  str(sanitize(row["snow"]))
            },
            "geometry": {"type": "Point",
                         "coordinates": [row['st_x'], row['st_y']]
                         }
        })
    return json.dumps(data)


def main():
    ''' see how we are called '''
    field = cgi.FieldStorage()
    dt = field.getfirst('dt', datetime.date.today().strftime("%Y-%m-%d"))
    ts = datetime.datetime.strptime(dt, '%Y-%m-%d')
    cb = field.getfirst('callback', None)
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")

    mckey = "/geojson/snowfall/%s?callback=%s" % (ts.strftime("%Y%m%d"),
                                                  cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = get_data(ts)
        mc.set(mckey, res, 300)
    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))

if __name__ == '__main__':
    main()
