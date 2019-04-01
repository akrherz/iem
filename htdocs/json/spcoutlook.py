#!/usr/bin/env python
"""SPC Outlook JSON service
"""
import datetime
import os
import cgi
import json

import memcache
import pytz
from pandas.io.sql import read_sql
from pyiem.nws.products.spcpts import THRESHOLD_ORDER
from pyiem.util import get_dbconn, ssw

ISO9660 = '%Y-%m-%dT%H:%MZ'


def get_order(threshold):
    """Lookup a threshold and get its rank, higher is more extreme"""
    if threshold not in THRESHOLD_ORDER:
        return -1
    return THRESHOLD_ORDER.index(threshold)


def get_dbcursor():
    """Do as I say"""
    postgis = get_dbconn('postgis')
    return postgis.cursor()


def dotime(time, lon, lat, day, cat):
    """Query for Outlook based on some timestamp"""
    if time in ['', 'current', 'now']:
        ts = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        if day > 1:
            ts += datetime.timedelta(days=(day - 1))
    else:
        # ISO formatting
        ts = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%MZ')
        ts = ts.replace(tzinfo=pytz.utc)
    pgconn = get_dbconn('postgis')
    df = read_sql("""
    SELECT issue at time zone 'UTC' as i,
    expire at time zone 'UTC' as e,
    valid at time zone 'UTC' as v,
    threshold, category from spc_outlooks where
    valid = (
        select valid from spc_outlooks where
        issue <= %s and expire > %s and day = %s
        and outlook_type = 'C' ORDER by valid DESC LIMIT 1)
    and ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
    and day = %s and outlook_type = 'C' and category = %s
    """, pgconn, params=(ts, ts, day, lon, lat, day, cat), index_col=None)
    res = {
        'generation_time': datetime.datetime.utcnow().strftime(ISO9660),
        'query_params': {
            'time': ts.strftime(ISO9660),
            'lon': lon,
            'lat': lat,
            'cat': cat,
            'day': day
            },
        'outlook': {}
        }
    if df.empty:
        return json.dumps(res)
    df['threshold_rank'] = df['threshold'].apply(get_order)
    df.sort_values('threshold_rank', ascending=False, inplace=True)
    res['outlook'] = {
        'threshold': df.iloc[0]['threshold'],
        'utc_valid': df.iloc[0]['v'].strftime(ISO9660),
        'utc_issue': df.iloc[0]['i'].strftime(ISO9660),
        'utc_expire': df.iloc[0]['e'].strftime(ISO9660),
        }
    return json.dumps(res)


def dowork(lon, lat, last, day, cat):
    """ Actually do stuff"""
    cursor = get_dbcursor()

    res = dict(outlooks=[])

    cursor.execute("""
    WITH data as (
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        valid at time zone 'UTC' as v,
        o.threshold, category, h.priority,
        row_number() OVER (PARTITION by expire
            ORDER by priority DESC NULLS last, issue ASC) as rank,
        case when o.threshold = 'SIGN' then rank()
            OVER (PARTITION by o.threshold, expire
            ORDER by valid ASC) else 2 end as sign_rank
        from spc_outlooks o LEFT JOIN spc_outlook_thresholds h on
        (o.threshold = h.threshold) where
        ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
        and day = %s and outlook_type = 'C' and category = %s
        and o.threshold not in ('TSTM') ORDER by issue DESC)
    SELECT i, e, v, threshold, category from data
    where (rank = 1 or sign_rank = 1)
    ORDER by e DESC
    """, (lon, lat, day, cat))
    running = {}
    for row in cursor:
        if last > 0:
            running.setdefault(row[3], 0)
            running[row[3]] += 1
            if running[row[3]] > last:
                continue
        res['outlooks'].append(
            dict(day=day,
                 utc_issue=row[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                 utc_expire=row[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                 utc_valid=row[2].strftime("%Y-%m-%dT%H:%M:%SZ"),
                 threshold=row[3],
                 category=row[4]))

    return json.dumps(res)


def main():
    """Do Main Stuff"""
    ssw("Content-type: application/vnd.geo+json\n\n")

    form = cgi.FieldStorage()
    lat = float(form.getfirst('lat', 42.0))
    lon = float(form.getfirst('lon', -95.0))
    time = form.getfirst('time')
    last = int(form.getfirst('last', 0))
    day = int(form.getfirst('day', 1))
    cat = form.getfirst('cat', 'categorical').upper()

    cb = form.getfirst('callback', None)

    hostname = os.environ.get("SERVER_NAME", "")
    mckey = ("/json/spcoutlook/%.4f/%.4f/%s/%s/%s/%s"
             ) % (lon, lat, last, day, cat, time)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey) if hostname != 'iem.local' else None
    if not res:
        if time is not None:
            res = dotime(time, lon, lat, day, cat)
        else:
            res = dowork(lon, lat, last, day, cat)
        mc.set(mckey, res, 3600)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
