#!/usr/bin/env python
''' Produce geojson of ISUSM data '''
import cgi
import sys
import psycopg2.extras
import datetime
from pyiem.datatypes import temperature
from pyiem.network import Table as NetworkTable
from pyiem.tracker import loadqc
import pytz
import json
ISUAG = psycopg2.connect(database='isuag', host='iemdb', user='nobody')
cursor = ISUAG.cursor(cursor_factory=psycopg2.extras.DictCursor)

IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
iemcursor = IEM.cursor()


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


def safe_t(val, units="C"):
    ''' '''
    if val is None:
        return 'M'
    return '%.1f' % (temperature(val, units).value('F'),)


def safe_p(val):
    ''' precipitation '''
    if val is None or val < 0:
        return 'M'
    return '%.2f' % (val / 25.4,)


def safe(val, precision):
    ''' safe precision formatter '''
    if val is None or val < 0:
        return 'M'
    return round(val, precision)


def safe_m(val):
    '''  '''
    if val is None or val < 0:
        return 'M'
    return round(val * 100., 0)


def get_data(ts):
    """ Get the data for this timestamp """
    qcdict = loadqc()
    nt = NetworkTable("ISUSM")
    data = {"type": "FeatureCollection",
            "crs": {"type": "EPSG",
                    "properties": {"code": 4326,
                                   "coordinate_order": [1, 0]}},
            "features": []}
    # Fetch the daily values
    iemcursor.execute("""
    SELECT id, pday, max_tmpf, min_tmpf from summary s JOIN stations t
    on (t.iemid = s.iemid) WHERE t.network = 'ISUSM' and day = %s
    """, (ts.date(),))
    daily = {}
    for row in iemcursor:
        daily[row[0]] = {'pday': row[1], 'max_tmpf': row[2],
                         'min_tmpf': row[3]}
    cursor.execute("""
    SELECT * from sm_hourly where valid = %s
    """, (ts,))
    for i, row in enumerate(cursor):
        sid = row['station']
        lon = nt.sts[sid]['lon']
        lat = nt.sts[sid]['lat']
        q = qcdict.get(sid, {})
        data['features'].append({"type": "Feature",
                                 "id": sid, "properties": {
            "encrh_avg": "%s%%" % safe(row['encrh_avg'], 1) if row['encrh_avg'] > 0 else "M",
            "rh":  "%.0f%%" % (row["rh"],),
            "hrprecip" : safe_p(row['rain_mm_tot']) if not q.get('precip', False) else 'M',
            "et": safe_p(row['etalfalfa']),
            "bat": safe(row['battv_min'], 2),
            "radmj": safe(row['slrmj_tot'], 2),
            "tmpf": safe_t(row['tair_c_avg']),
            "high": safe_t(daily.get(sid, {}).get('max_tmpf', None), 'F'),
            "low": safe_t(daily.get(sid, {}).get('min_tmpf', None), 'F'),
            "pday": safe(daily.get(sid, {}).get('pday', None), 2) if not q.get('precip', False) else 'M',
            "soil04t": safe_t(row['tsoil_c_avg']) if not q.get('soil4', False) else 'M',
            "soil12t": safe_t(row['t12_c_avg']),
            "soil24t": safe_t(row['t24_c_avg']),
            "soil50t": safe_t(row['t50_c_avg']),
            "soil12m": safe_m(row['vwc_12_avg']),
            "soil24m": safe_m(row['vwc_24_avg']),
            "soil50m": safe_m(row['vwc_50_avg']),
            "gust": safe(row['ws_mph_max'], 1),
            "wind": "%s@%.0f" % (drct2txt(row['winddir_d1_wvt']),
                                 row['ws_mps_s_wvt'] * 2.23),
            'name': nt.sts[sid]['name']
            },
            "geometry": {"type": "Point",
                         "coordinates": [lon, lat]
                         }
        })
    sys.stdout.write(json.dumps(data))


def main(argv):
    """Go Main Go"""
    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")
    field = cgi.FieldStorage()
    dt = field.getfirst('dt')
    ts = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.000Z')
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    get_data(ts)

if __name__ == '__main__':
    # see how we are called
    main(sys.argv)
