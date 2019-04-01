#!/usr/bin/env python
"""JSON service emitting observation history for a given date"""
import json
import os
import datetime
import cgi

from pandas.io.sql import read_sql
from dateutil.parser import parse
import memcache
from pyiem.reference import IEMVARS
from pyiem.util import get_dbconn, ssw


def do_today(table, station, network, date):
    """Our backend is current_log"""
    pgconn = get_dbconn('iem')
    cols = ['local_valid', 'utc_valid', 'tmpf', 'sknt', 'gust', 'drct']
    table['fields'] = [IEMVARS[col] for col in cols]
    df = read_sql("""
        select
        to_char(valid at time zone tzname,
                'YYYY-MM-DDThh24:MI:SS') as local_valid,
        to_char(valid at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as utc_valid,
        tmpf, sknt, gust, drct from current_log c JOIN stations t
        on (c.iemid = t.iemid) WHERE date(valid at time zone tzname) = %s
        and t.id = %s and t.network = %s ORDER by local_valid
    """, pgconn, params=(date, station, network), index_col=None)
    table['rows'] = [row for row in df.itertuples(index=False)]


def do_asos(table, station, _network, date):
    """Our backend is ASOS"""
    pgconn = get_dbconn('asos')
    cols = ['local_valid', 'utc_valid', 'tmpf', 'sknt', 'gust', 'drct']
    table['fields'] = [IEMVARS[col] for col in cols]
    df = read_sql("""
        select
        to_char(valid at time zone tzname,
                'YYYY-MM-DDThh24:MI:SS') as local_valid,
        to_char(valid at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as utc_valid,
        tmpf, sknt, gust, drct from alldata a JOIN stations t
        on (a.station = t.id) WHERE date(valid at time zone tzname) = %s
        and station = %s ORDER by local_valid
    """, pgconn, params=(date, station), index_col=None)
    table['rows'] = [row for row in df.itertuples(index=False)]


def workflow(station, network, date):
    """ Go get the dictionary of data we need and deserve """
    date = parse(date).date()
    table = {'fields': [], 'rows': []}
    if date == datetime.date.today():
        do_today(table, station, network, date)
    elif network == 'AWOS' or network.find("ASOS") > -1:
        do_asos(table, station, network, date)

    return json.dumps(table)


def main():
    """ Do something, one time """
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    station = form.getfirst("station", 'AMW')
    network = form.getfirst("network", "IA_ASOS")
    date = form.getfirst('date', '2016-01-01')
    cb = form.getfirst("callback", None)

    hostname = os.environ.get("SERVER_NAME", "")
    mckey = "/json/obhistory/%s/%s/%s" % (station, network, date)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey) if hostname != 'iem.local' else None
    if not res:
        res = workflow(station, network, date).replace("NaN", "null")
        mc.set(mckey, res, 3600)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
