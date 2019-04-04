#!/usr/bin/env python
""" Produce geojson of CLI data """
import cgi
import datetime
import json
from json import encoder
import memcache
import psycopg2.extras
from pyiem.util import get_dbconn, ssw
from pyiem.reference import TRACE_VALUE
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


def departure(ob, climo):
    """ Compute a departure value """
    if ob is None or climo is None:
        return "M"
    return ob - climo


def sanitize(val):
    """ convert to Ms"""
    if val is None:
        return "M"
    if val == TRACE_VALUE:
        return "T"
    return val


def get_data(ts, fmt):
    """ Get the data for this timestamp """
    pgconn = get_dbconn('iem')
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    data = {"type": "FeatureCollection",
            "features": []}
    # Fetch the daily values
    cursor.execute("""
    select station, name, product, state, wfo,
    round(st_x(geom)::numeric, 4)::float as st_x,
    round(st_y(geom)::numeric, 4)::float as st_y,
    high, high_normal, high_record, high_record_years,
    low, low_normal, low_record, low_record_years,
    precip, precip_month, precip_jan1, precip_jan1_normal,
    precip_jul1, precip_dec1, precip_dec1_normal, precip_record,
    precip_month_normal, snow, snow_month, snow_jun1, snow_jul1,
    snow_dec1, snow_record, snow_jul1_normal,
    snow_dec1_normal, snow_month_normal, precip_jun1, precip_jun1_normal,
    round(((case when snow_jul1 < 0.1 then 0 else snow_jul1 end)
        - snow_jul1_normal)::numeric, 2) as snow_jul1_depart
    from cli_data c JOIN stations s on (c.station = s.id)
    WHERE s.network = 'NWSCLI' and c.valid = %s
    """, (ts.date(),))
    for i, row in enumerate(cursor):
        data['features'].append({"type": "Feature", "id": i, "properties": {
                "station": row["station"],
                "state": row["state"],
                "wfo": row["wfo"],
                "link": "/api/1/nwstext.txt?pid=%s" % (row['product'],),
                "name": row["name"],
                "high":  str(sanitize(row["high"])),
                "high_record":  str(sanitize(row["high_record"])),
                "high_record_years":  row["high_record_years"],
                "high_normal":  str(sanitize(row["high_normal"])),
                "high_depart": departure(row['high'], row['high_normal']),
                "low":  str(sanitize(row["low"])),
                "low_record":  str(sanitize(row["low_record"])),
                "low_record_years":  row["low_record_years"],
                "low_normal":  str(sanitize(row["low_normal"])),
                "low_depart": departure(row['low'], row['low_normal']),
                "precip":  str(sanitize(row["precip"])),
                "precip_month":  str(sanitize(row["precip_month"])),
                "precip_month_normal":  str(
                    sanitize(row["precip_month_normal"])),
                "precip_jan1":  str(sanitize(row["precip_jan1"])),
                "precip_jan1_normal": str(sanitize(row["precip_jan1_normal"])),
                "precip_jun1":  str(sanitize(row["precip_jun1"])),
                "precip_jun1_normal": str(sanitize(row["precip_jun1_normal"])),
                "precip_jul1":  str(sanitize(row["precip_jul1"])),
                "precip_dec1":  str(sanitize(row["precip_dec1"])),
                "precip_dec1_normal": str(sanitize(row["precip_dec1_normal"])),
                "precip_record":  str(sanitize(row["precip_record"])),
                "snow":  str(sanitize(row["snow"])),
                "snow_month":  str(sanitize(row["snow_month"])),
                "snow_jun1":  str(sanitize(row["snow_jun1"])),
                "snow_jul1":  str(sanitize(row["snow_jul1"])),
                "snow_dec1":  str(sanitize(row["snow_dec1"])),
                "snow_record":  str(sanitize(row["snow_record"])),
                "snow_jul1_normal":  str(sanitize(row["snow_jul1_normal"])),
                "snow_jul1_depart":  str(sanitize(row["snow_jul1_depart"])),
                "snow_dec1_normal":  str(sanitize(row["snow_dec1_normal"])),
                "snow_month_normal":  str(sanitize(row["snow_month_normal"])),
            },
            "geometry": {"type": "Point",
                         "coordinates": [row['st_x'], row['st_y']]
                         }
        })
    if fmt == 'geojson':
        return json.dumps(data)
    cols = ("station,name,state,wfo,high,high_record,high_record_years,"
            "high_normal,low,low_record,low_record_years,low_normal,"
            "precip,precip_month,precip_jan1,precip_jan1_normal,"
            "precip_jul1,precip_dec1,precip_dec1_normal,precip_record,"
            "snow,snow_month,snow_jun1,snow_jul1,snow_dec1,snow_record,"
            "snow_jul1_normal,snow_dec1_normal,"
            "snow_month_normal,snow_jul1_depart")
    res = cols+"\n"
    for feat in data['features']:
        for col in cols.split(","):
            val = feat['properties'][col]
            if isinstance(val, (list, tuple)):
                res += "%s," % (" ".join([str(s) for s in val]), )
            else:
                res += "%s," % (val,)
        res += "\n"
    return res


def main():
    ''' see how we are called '''
    field = cgi.FieldStorage()
    dt = field.getfirst('dt', datetime.date.today().strftime("%Y-%m-%d"))
    ts = datetime.datetime.strptime(dt, '%Y-%m-%d')
    cb = field.getfirst('callback', None)
    fmt = field.getfirst('fmt', 'geojson')

    if fmt == 'geojson':
        ssw("Content-type: application/vnd.geo+json\n\n")
    else:
        ssw("Content-type: text/plain\n\n")

    mckey = "/geojson/cli/%s?callback=%s&fmt=%s" % (ts.strftime("%Y%m%d"),
                                                    cb, fmt)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = get_data(ts, fmt)
        mc.set(mckey, res, 300)
    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
