#!/usr/bin/env python
"""
 Tile Map service metadata
"""
import memcache
import sys
import cgi
import os


def run():
    """ Generate json response """
    import json
    import datetime
    ISO = "%Y-%m-%dT%H:%M:%SZ"
    res = {'generation_utc_time':
           datetime.datetime.utcnow().strftime(ISO),
           'services': []
           }
    j = json.load(open('/home/ldm/data/gis/images/4326/USCOMP/n0q_0.json'))
    vt = datetime.datetime.strptime(j['meta']['valid'], ISO)
    res['services'].append({
            'id': 'ridge_uscomp_n0q',
            'layername': 'ridge::USCOMP-N0Q-%s' % vt.strftime("%Y%m%d%H%M"),
            'utc_valid': j['meta']['valid']
            })

    j = json.load(open('/home/ldm/data/gis/images/4326/USCOMP/n0r_0.json'))
    vt = datetime.datetime.strptime(j['meta']['valid'], ISO)
    res['services'].append({
            'id': 'ridge_uscomp_n0r',
            'layername': 'ridge::USCOMP-N0R-%s' % vt.strftime("%Y%m%d%H%M"),
            'utc_valid': j['meta']['valid']
            })

    return json.dumps(res)

if __name__ == '__main__':
    sys.stdout.write("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    if os.environ['REQUEST_METHOD'] not in ['GET', 'POST']:
        sys.stdout.write("Content-type: text/plain\n\n")
        sys.stdout.write("HTTP METHOD NOT ALLOWED")
        return
    cb = form.getfirst('callback', None)

    mckey = "/json/tms.json"
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 15)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))
