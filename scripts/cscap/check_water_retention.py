"""Make sure that the water retention values are going in the right order"""
import psycopg2
import pandas as pd
from pandas.io.sql import read_sql

G2L = ['SOIL2', 'SOIL39', 'SOIL41', 'SOIL34', 'SOIL29', 'SOIL30', 'SOIL31',
       'SOIL35', 'SOIL33', 'SOIL42', 'SOIL32']

LABELS = ['0bar', 'free', '0.01', '0.03', '0.05', '0.10', '0.33',
          '1.0', '3.0', '3.9', '15.0']

pgconn = psycopg2.connect(database='sustainablecorn', host='iemdb',
                          user='nobody')
df = read_sql("""SELECT site, plotid, depth, varname, year,
    value::numeric as value,
    subsample from soil_data
    WHERE value is not null and
    value not in ('outlier', 'Farm was not available', 'Farm sold',
    'n/a', 'did not collect', '.', 'Not collected', 'N/A')
    and varname in ('SOIL2', 'SOIL39', 'SOIL41', 'SOIL29', 'SOIL34', 'SOIL30',
    'SOIL31', 'SOIL35', 'SOIL33', 'SOIL42', 'SOIL32')
    """, pgconn, index_col=None)

df = pd.pivot_table(df, values='value', index=['site', 'plotid', 'depth',
                                               'year',
                                               'subsample'],
                    columns=['varname'])
for i, varname in enumerate(G2L[:-1]):
    for j in range(i+1, len(G2L)):
        varname2 = G2L[j]
        df2 = df[df[varname] < df[varname2]]
        for k, row in df2.iterrows():
            print(("%s,%s,%s,%s,%s,%s (%s),%.3f,%s (%s),%.3f"
                   ) % (k[0], k[1], k[2], k[3], k[4], varname, LABELS[i],
                        row[varname], varname2, LABELS[j], row[varname2]))
