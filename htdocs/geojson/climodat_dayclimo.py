#!/usr/bin/env python
"""Dump daily computed climatology direct from the database"""
import cgi
import datetime
import json

import memcache
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, ssw


def run(network, month, day, syear, eyear):
    """Do something"""
    pgconn = get_dbconn('coop')
    cursor = pgconn.cursor()

    nt = NetworkTable(network)
    sday = "%02i%02i" % (month, day)
    table = "alldata_%s" % (network[:2],)
    cursor.execute("""
    WITH data as (
      SELECT station, year, precip,
      avg(precip) OVER (PARTITION by station) as avg_precip,
      high, rank() OVER (PARTITION by station ORDER by high DESC) as max_high,
      avg(high) OVER (PARTITION by station) as avg_high,
      rank() OVER (PARTITION by station ORDER by high ASC) as min_high,
      low, rank() OVER (PARTITION by station ORDER by low DESC) as max_low,
      avg(low) OVER (PARTITION by station) as avg_low,
      rank() OVER (PARTITION by station ORDER by low ASC) as min_low,
      rank() OVER (PARTITION by station ORDER by precip DESC) as max_precip
      from """ + table + """ WHERE sday = %s and year >= %s and year < %s),

    max_highs as (
      SELECT station, high, array_agg(year) as years from data
      where max_high = 1 GROUP by station, high),
    min_highs as (
      SELECT station, high, array_agg(year) as years from data
      where min_high = 1 GROUP by station, high),

    max_lows as (
      SELECT station, low, array_agg(year) as years from data
      where max_low = 1 GROUP by station, low),
    min_lows as (
      SELECT station, low, array_agg(year) as years from data
      where min_low = 1 GROUP by station, low),

    max_precip as (
      SELECT station, precip, array_agg(year) as years from data
      where max_precip = 1 GROUP by station, precip),

    avgs as (
      SELECT station, count(*) as cnt, max(avg_precip) as p,
      max(avg_high) as h, max(avg_low) as l from data GROUP by station)

    SELECT a.station, a.cnt, a.h, xh.high, xh.years,
    nh.high, nh.years, a.l, xl.low, xl.years,
    nl.low, nl.years, a.p, mp.precip, mp.years
    from avgs a, max_highs xh, min_highs nh, max_lows xl, min_lows nl,
    max_precip mp
    WHERE xh.station = a.station and xh.station = nh.station
    and xh.station = xl.station and
    xh.station = nl.station and xh.station = mp.station ORDER by station ASC

    """, (sday, syear, eyear))
    data = {"type": "FeatureCollection",
            "month": month, "day": day, "network": network,
            "crs": {"type": "EPSG",
                    "properties": {"code": 4326,
                                   "coordinate_order": [1, 0]}},
            "features": []}

    for i, row in enumerate(cursor):
        if row[0] not in nt.sts:
            continue
        props = dict(station=row[0], years=row[1],
                     avg_high=float(row[2]), max_high=row[3],
                     max_high_years=row[4], min_high=row[5],
                     min_high_years=row[6],
                     avg_low=float(row[7]), max_low=row[8],
                     max_low_years=row[9], min_low=row[10],
                     min_low_years=row[11],
                     avg_precip=float(row[12]),
                     max_precip=row[13],
                     max_precip_years=row[14])
        data['features'].append({"type": "Feature", "id": i,
                                 'properties': props,
                                 "geometry": {"type": "Point",
                                              "coordinates": [
                                                        nt.sts[row[0]]['lon'],
                                                        nt.sts[row[0]]['lat']]
                                              }
                                 })

    return json.dumps(data)


def main():
    """Main()"""
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    network = form.getfirst("network", "IACLIMATE").upper()
    month = int(form.getfirst('month', 1))
    day = int(form.getfirst('day', 1))
    syear = int(form.getfirst('syear', 1800))
    eyear = int(form.getfirst('eyear', datetime.datetime.now().year + 1))
    cb = form.getfirst('callback', None)

    mckey = "/geojson/climodat_dayclimo/%s/%s/%s/%s/%s" % (network, month, day,
                                                           syear, eyear)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(network, month, day, syear, eyear)
        mc.set(mckey, res, 86400)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
