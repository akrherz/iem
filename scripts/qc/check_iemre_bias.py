"""Look to see if we have something systematic wrong with IEMRE"""
import requests
import json
from pyiem.network import Table as NetworkTable
import psycopg2
import pandas as pd
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database='iem', host='iemdb', user='nobody')
cursor = pgconn.cursor()

nt = NetworkTable("WI_ASOS")

df = read_sql("""
    SELECT day, max_tmpf, min_tmpf from summary_2016 s JOIN stations t
    ON (s.iemid = t.iemid) WHERE t.network = 'WI_ASOS' and t.id = 'LSE'
    ORDER by day ASC""", pgconn, index_col='day')

uri = ("http://mesonet.agron.iastate.edu/iemre/multiday/2016-01-01/"
       "2016-07-19/%.2f/%.2f/json"
       ) % (nt.sts['LSE']['lat'], nt.sts['LSE']['lon'])
r = requests.get(uri)
j = json.loads(r.content)

idf = pd.DataFrame(j['data'])
idf['day'] = pd.to_datetime(idf['date'])
idf.set_index('day', inplace=True)

idf['ob_high'] = df['max_tmpf']
idf['ob_low'] = df['min_tmpf']

idf['high_delta'] = idf['ob_high'] - idf['daily_high_f']
idf['low_delta'] = idf['ob_low'] - idf['daily_low_f']
idf.sort_values('low_delta', inplace=True)

print idf[['ob_low', 'daily_low_f']].head()
print idf[['ob_low', 'daily_low_f']].tail()
