#!/usr/bin/env python
"""JSON service that emits RAOB profiles in JSON format

{'profiles': [
  {
  'station': 'OAX',
  'valid': '2013-08-21T12:00:00Z',
  'profile': [
    {'tmpc':99, 'pres': 99, 'dwpc': 99, 'sknt': 99, 'drct': 99, 'hght': 99},
    {'tmpc':99, 'pres': 99, 'dwpc': 99, 'sknt': 99, 'drct': 99, 'hght': 99},
    {...}
              ]
  },
  {...}]
}
"""
import cgi
import datetime
import json
# http://stackoverflow.com/questions/1447287
from json import encoder

import pytz
import memcache
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, ssw
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


def safe(val):
    """Be careful """
    if val is None:
        return None
    return float(val)


def run(ts, sid, pressure):
    """ Actually do some work! """
    dbconn = get_dbconn('postgis')

    res = {'profiles': []}
    table = 'raob_profile_%s' % (ts.year,)
    if ts.year > datetime.datetime.utcnow().year or ts.year < 1946:
        return json.dumps(res)

    stationlimiter = ''
    if sid != '':
        stationlimiter = " f.station = '%s' and " % (sid, )
    pressurelimiter = ''
    if pressure > 0:
        pressurelimiter = " and p.pressure = %s " % (pressure, )
    df = read_sql("""
        SELECT f.station, p.pressure, p.height,
        round(p.tmpc::numeric,1) as tmpc,
        round(p.dwpc::numeric,1) as dwpc, p.drct,
        round((p.smps * 1.94384)::numeric,0) as sknt from """ + table + """
        p JOIN raob_flights f
        on (p.fid = f.fid) WHERE
        """ + stationlimiter + """ f.valid = %s """ + pressurelimiter + """
        ORDER by f.station, p.pressure DESC
        """, dbconn, params=(ts, ), index_col=None)
    for station, gdf in df.groupby('station'):
        profile = []
        for _, row in gdf.iterrows():
            profile.append(dict(pres=safe(row['pressure']),
                                hght=safe(row['height']),
                                tmpc=safe(row['tmpc']),
                                dwpc=safe(row['dwpc']),
                                drct=safe(row['drct']),
                                sknt=safe(row['sknt'])))
        res['profiles'].append(dict(station=station,
                                    valid=ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    profile=profile))
    dbconn.close()
    return json.dumps(res)


def parse_time(tstring):
    """Allow for various timestamp formats"""
    if tstring is None or tstring == '':
        tstring = '201308211200'
    if tstring.find("T") > 0:
        # Assume ISO
        dt = datetime.datetime.strptime(tstring[:16], '%Y-%m-%dT%H:%M')
    else:
        dt = datetime.datetime.strptime(tstring[:12], '%Y%m%d%H%M')

    return dt.replace(tzinfo=pytz.utc)


def main():
    """Do Something"""
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    sid = form.getfirst('station', '')[:4]
    if len(sid) == 3:
        sid = "K"+sid
    ts = parse_time(form.getfirst('ts'))
    pressure = int(form.getfirst('pressure', -1))
    cb = form.getfirst('callback', None)

    mckey = "/json/raob/%s/%s/%s?callback=%s" % (ts.strftime("%Y%m%d%H%M"),
                                                 sid, pressure, cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(ts, sid, pressure)
        mc.set(mckey, res)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cgi.escape(cb, quote=True), res))


if __name__ == '__main__':
    main()
