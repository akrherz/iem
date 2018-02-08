#!/usr/bin/env python
"""Do a comparison with what's on CRH CAP"""
from __future__ import print_function
import datetime
import sys
import urllib2

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.nws.vtec import VTEC_SIGNIFICANCE, VTEC_PHENOMENA
from pyiem.util import get_dbconn

URI = "https://www.weather.gov/source/crh/allhazard.geojson"

REV_VTEC_SIGNIFIANCE = dict((v, k) for k, v in VTEC_SIGNIFICANCE.items())
REV_VTEC_PHENOMENA = dict((v, k) for k, v in VTEC_PHENOMENA.items())


def get_phenomena(value):
    if value == 'Rip Current':
        return 'RP'
    return REV_VTEC_PHENOMENA.get(value, value)


def get_significance(value):
    return REV_VTEC_SIGNIFIANCE.get(value, value)


def main():
    """Go Main Go"""
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write("Report run at %s\n" % (datetime.datetime.utcnow(), ))
    sys.stdout.write("Comparing %s\n" % (URI, ))
    try:
        req = requests.get(URI)
        jdata = req.json()
    except urllib2.HTTPError as _exp:
        sys.stdout.write("Failure to download %s, comparison failed" % (URI, ))
        return
    rows = []
    for feature in jdata['features']:
        props = feature['properties']
        rows.append(dict(wfo=props['office'][1:],
                         phenomena=get_phenomena(props['phenomenon']),
                         significance=get_significance(props['significance']),
                         eventid=int(props['etn'])))
    capdf = pd.DataFrame(rows)

    iemdf = read_sql("""
    SELECT distinct wfo, phenomena, significance, eventid from warnings
    where expire > now()
    """, get_dbconn('postgis', user='nobody'), index_col=None)
    for _idx, row in capdf.iterrows():
        df2 = iemdf[((iemdf['phenomena'] == row['phenomena']) &
                     (iemdf['significance'] == row['significance']) &
                     (iemdf['eventid'] == row['eventid']) &
                     (iemdf['wfo'] == row['wfo']))]
        if df2.empty:
            if len(row['phenomena']) > 2:
                print(("Indeteriminate %s %s %s %s"
                       ) % (row['wfo'], row['phenomena'], row['significance'],
                            row['eventid']))
                continue
            print(("IEM MISSING (%s %s %s %s)"
                   ) % (row['wfo'], row['phenomena'], row['significance'],
                        row['eventid']))

    for _idx, row in iemdf.iterrows():
        df2 = capdf[((capdf['phenomena'] == row['phenomena']) &
                     (capdf['significance'] == row['significance']) &
                     (capdf['eventid'] == row['eventid']) &
                     (capdf['wfo'] == row['wfo']))]
        if df2.empty:
            print(("CAP MISSING (%s %s %s %s)"
                   ) % (row['wfo'], row['phenomena'], row['significance'],
                        row['eventid']))

    sys.stdout.write("DONE...\n")


if __name__ == '__main__':
    main()
