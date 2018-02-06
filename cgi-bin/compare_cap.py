#!/usr/bin/env python
"""Do a comparison with what's on api.weather.gov/cap"""
from __future__ import print_function
import datetime
import sys
import urllib2

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.nws.vtec import parse as vtec_parse
from pyiem.util import get_dbconn

CAP = "https://api.weather.gov/alerts/active"


def main():
    """Go Main Go"""
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write("Report run at %s\n" % (datetime.datetime.utcnow(), ))
    try:
        req = requests.get(CAP)
        jdata = req.json()
    except urllib2.HTTPError as _exp:
        sys.stdout.write("Failure to download %s, comparison failed" % (CAP, ))
        return
    rows = []
    for feature in jdata['features']:
        props = feature['properties']
        vtecstring = props.get('parameters', {}).get('VTEC')
        if vtecstring is None:
            continue
        vtec = vtec_parse(vtecstring[0])[0]
        for ugc in props['geocode']['UGC']:
            rows.append(dict(wfo=vtec.office,
                             phenomena=vtec.phenomena,
                             significance=vtec.significance,
                             eventid=vtec.etn,
                             ugc=ugc))
    capdf = pd.DataFrame(rows)

    iemdf = read_sql("""
    SELECT wfo, phenomena, significance, eventid, ugc from warnings
    where expire > now()
    """, get_dbconn('postgis', user='nobody'), index_col=None)
    for _idx, row in capdf.iterrows():
        df2 = iemdf[((iemdf['phenomena'] == row['phenomena']) &
                     (iemdf['significance'] == row['significance']) &
                     (iemdf['eventid'] == row['eventid']) &
                     (iemdf['wfo'] == row['wfo']) &
                     (iemdf['ugc'] == row['ugc']))]
        if df2.empty:
            print(("IEM MISSING (%s %s %s %s %s)"
                   ) % (row['wfo'], row['phenomena'], row['significance'],
                        row['eventid'], row['ugc']))

    for _idx, row in iemdf.iterrows():
        df2 = capdf[((capdf['phenomena'] == row['phenomena']) &
                     (capdf['significance'] == row['significance']) &
                     (capdf['eventid'] == row['eventid']) &
                     (capdf['wfo'] == row['wfo']) &
                     (capdf['ugc'] == row['ugc']))]
        if df2.empty:
            print(("CAP MISSING (%s %s %s %s %s)"
                   ) % (row['wfo'], row['phenomena'], row['significance'],
                        row['eventid'], row['ugc']))

    sys.stdout.write("DONE...\n")


if __name__ == '__main__':
    main()
