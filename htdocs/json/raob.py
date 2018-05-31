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
from pyiem.util import get_dbconn, ssw
encoder.FLOAT_REPR = lambda o: format(o, '.2f')


def safe(val):
    """Be careful """
    if val is None:
        return None
    return float(val)


def run(ts, sid):
    """ Actually do some work! """
    dbconn = get_dbconn('postgis')
    cursor = dbconn.cursor()

    res = {'profiles': []}
    table = 'raob_profile_%s' % (ts.year,)
    if ts.year > datetime.datetime.utcnow().year or ts.year < 1946:
        return json.dumps(res)

    cursor.execute("""
        SELECT p.pressure, p.height,
        round(p.tmpc::numeric,1),
        round(p.dwpc::numeric,1), p.drct,
        round((p.smps * 1.94384)::numeric,0) from """ + table + """
        p JOIN raob_flights f
        on (p.fid = f.fid) WHERE
        f.station = %s and f.valid = %s ORDER by p.pressure DESC
        """, (sid, ts))
    profile = []
    for row in cursor:
        profile.append(dict(pres=safe(row[0]),
                            hght=safe(row[1]),
                            tmpc=safe(row[2]),
                            dwpc=safe(row[3]),
                            drct=safe(row[4]),
                            sknt=safe(row[5])))
    res['profiles'].append(dict(station=sid,
                                valid=ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                profile=profile))
    cursor.close()
    dbconn.close()
    return json.dumps(res)


def main():
    """Do Something"""
    ssw("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    sid = form.getfirst('station', 'KOAX')[:4]
    if len(sid) == 3:
        sid = "K"+sid
    ts = form.getfirst('ts', '201308211200')[:12]
    cb = form.getfirst('callback', None)

    mckey = "/json/raob/%s/%s?callback=%s" % (ts, sid, cb)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        ts = datetime.datetime.strptime(ts, '%Y%m%d%H%M')
        ts = ts.replace(tzinfo=pytz.utc)
        res = run(ts, sid)
        mc.set(mckey, res)

    if cb is None:
        ssw(res)
    else:
        ssw("%s(%s)" % (cb, res))


if __name__ == '__main__':
    main()
