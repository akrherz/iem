#!/usr/bin/env python
"""
Dump some stats useful for website geeks
"""
import rrdtool
import json
import datetime
import sys

j = {'stats': {}, 'valid': datetime.datetime.utcnow().strftime(
                                                    "%Y-%m-%dT%H:%M:%SZ")}


def get_reqs():
    count = 0
    for i in range(100, 109):
        fn = "/var/lib/pnp4nagios/iemvs%03i/Apache_Stats_II.rrd" % (i,)
        ts = rrdtool.last(fn)
        data = rrdtool.fetch(fn,
                             "AVERAGE", "-s", str(ts - 300), "-e", str(ts))
        samples = data[2]
        if len(samples) < 2:
            continue
        count += samples[-2][13]

    j['stats']['apache_req_per_sec'] = count


def get_bandwidth():
    fn = "/var/lib/pnp4nagios/mesonet/eth0.rrd"

    ts = rrdtool.last(fn)
    data = rrdtool.fetch(fn,
                         "AVERAGE", "-s", str(ts - 300), "-e", str(ts))
    samples = data[2]
    j['stats']['bandwidth'] = samples[-2][2]

get_reqs()
get_bandwidth()
sys.stdout.write("Content-type: text/plain\n\n")
sys.stdout.write(json.dumps(j))
