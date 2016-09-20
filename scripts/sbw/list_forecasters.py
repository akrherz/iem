import psycopg2
import pandas as pd
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database='postgis', host='localhost', port=5555,
                          user='nobody')

df = read_sql("""WITH data as (
    SELECT distinct wfo, eventid, extract(year from issue) as year,
    fcster from warnings where phenomena = 'FF' and significance = 'W'
    and issue > '2008-01-01' and fcster != '' and fcster is not null
    and wfo is not null)

    SELECT wfo, year, fcster, count(*) from data GROUP by wfo, year, fcster
    """, pgconn, index_col=None)

writer = pd.ExcelWriter('ffw_by_forecaster.xlsx')
wfos = df['wfo'].unique()
wfos.sort()
for wfo in wfos:
    sdf = df[df['wfo'] == wfo]
    pdf = sdf[['fcster', 'year', 'count']].pivot('fcster', 'year', 'count')
    pdf.to_excel(writer, wfo)
writer.save()
