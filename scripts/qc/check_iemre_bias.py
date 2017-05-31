"""Look to see if we have something systematic wrong with IEMRE"""
from __future__ import print_function
import json

import requests
from pyiem.network import Table as NetworkTable
import psycopg2
import pandas as pd
from pandas.io.sql import read_sql


def main():
    """Go Main Go"""
    pgconn = psycopg2.connect(database='iem', host='localhost',
                              port=5555, user='nobody')

    nt = NetworkTable("WI_ASOS")

    df = read_sql("""
        SELECT day, max_tmpf, min_tmpf, pday
        from summary_2017 s JOIN stations t
        ON (s.iemid = t.iemid) WHERE t.network = 'WI_ASOS' and t.id = 'MSN'
        ORDER by day ASC""", pgconn, index_col='day')

    uri = ("https://mesonet.agron.iastate.edu/iemre/multiday/2017-01-01/"
           "2017-05-30/%.2f/%.2f/json"
           ) % (nt.sts['MSN']['lat'], nt.sts['MSN']['lon'])
    req = requests.get(uri)
    j = json.loads(req.content)

    idf = pd.DataFrame(j['data'])
    idf['day'] = pd.to_datetime(idf['date'])
    idf.set_index('day', inplace=True)

    idf['ob_high'] = df['max_tmpf']
    idf['ob_low'] = df['min_tmpf']
    idf['ob_pday'] = df['pday']

    idf['high_delta'] = idf['ob_high'] - idf['daily_high_f']
    idf['low_delta'] = idf['ob_low'] - idf['daily_low_f']
    idf['precip_delta'] = idf['ob_pday'] - idf['daily_precip_in']
    idf.sort_values('precip_delta', inplace=True, ascending=True)

    print("IEMRE greater than Obs")
    print(idf[['ob_pday', 'daily_precip_in', 'precip_delta']].head())
    print("Obs greater than IEMRE")
    print(idf[['ob_pday', 'daily_precip_in', 'precip_delta']].tail())
    print("sum")
    print(idf[['ob_pday', 'daily_precip_in']].sum())


if __name__ == '__main__':
    main()
