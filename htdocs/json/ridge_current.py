#!/usr/bin/env python
"""
 Aggregate the RIDGE current files
"""
import memcache
import cgi
import sys

iso = "%Y-%m-%dT%H:%M:%SZ"


def run(product):
    ''' Actually run for this product '''
    import json
    import datetime
    import glob

    res = {'generation_time_utc': datetime.datetime.utcnow().strftime(iso),
           'product': product,
           'meta': []}

    for fn in glob.glob(("/home/ldm/data/gis/images/4326/"
                         "ridge/???/%s_0.json"
                         ) % (product,)):
        try:
            j = json.load(open(fn))
            res['meta'].append(j['meta'])
        except:
            pass

    return json.dumps(res)


def main():
    ''' See how we are called '''
    sys.stdout.write("Content-type: application/json\n\n")

    form = cgi.FieldStorage()
    product = form.getfirst('product', 'N0Q')[:3].upper()
    cb = form.getfirst('callback', None)

    mckey = "/json/ridge_current_%s.json" % (product, )
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(product)
        mc.set(mckey, res, 30)

    if cb is None:
        sys.stdout.write(res)
    else:
        sys.stdout.write("%s(%s)" % (cb, res))

if __name__ == '__main__':
    main()
