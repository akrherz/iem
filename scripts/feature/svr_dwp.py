import iemdb

ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

pcursor.execute("""
  SELECT date(issue) as d, count(*) as cnt from warnings WHERE
  phenomena in ('TO') and wfo in ('DMX','DVN','ARX','FSD','OAX')
  and significance = 'W'  and gtype = 'C' and extract(month from issue) = 4
  GROUP by d ORDER by cnt DESC LIMIT 20
""")

for row in pcursor:
  day = row[0]
  acursor.execute("""
   SELECT avg(dwpf) from t%s where station = 'DSM' and
   valid BETWEEN '%s 12:00' and '%s 21:00' and dwpf > -20""" % (day.year,
   day, day))
  row2 = acursor.fetchone()
  dsm = row2[0]

  acursor.execute("""
   SELECT avg(dwpf) from t%s where station = 'DBQ' and
   valid BETWEEN '%s 12:00' and '%s 21:00' and dwpf > -20""" % (day.year,
   day, day))
  row2 = acursor.fetchone()
  oma = row2[0]
  print '%s,%s,%.1f,%.1f' % (day, row[1], dsm, oma or 0)
