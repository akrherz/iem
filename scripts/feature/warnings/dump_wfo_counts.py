from pandas.io.sql import read_sql
import psycopg2
pgconn = psycopg2.connect(database='postgis', host='localhost', port=5555)

pd = read_sql("""WITH data as (
  SELECT distinct wfo, extract(year from issue) as yr,
  phenomena, significance from warnings where issue > '2005-01-01' and
  significance is not null and phenomena is not null)

  SELECT wfo, yr, count(*) from data GROUP by wfo, yr""", pgconn)

pd2 = pd.pivot_table(index=['wfo'], columns=['yr'])

pd2.to_excel('dump.xls')
