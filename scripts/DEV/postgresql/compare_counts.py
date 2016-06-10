import psycopg2

oldpg = psycopg2.connect(database='postgis', host='localhost', port=5555, user='mesonet')
cursor = oldpg.cursor()

dbs = []
cursor.execute("""SELECT datname FROM pg_database
WHERE datistemplate = false ORDER by datname""")
for row in cursor:
  dbs.append(row[0])

for db in dbs:
  if db <= 'cscap':
    continue
  print("running %s..." % (db,))
  oldpg = psycopg2.connect(database=db, host='localhost', port=5556, user='mesonet')
  ocursor = oldpg.cursor()
  newpg = psycopg2.connect(database=db, host='localhost', port=5555, user='mesonet')
  ncursor = newpg.cursor()

  tables = []
  ocursor.execute("""SELECT table_name
FROM information_schema.tables WHERE table_schema = 'public'
ORDER BY table_name""")
  for row in ocursor:
    tables.append(row[0])

  for table in tables:
    ocursor.execute("""SELECT count(*) from """+table)
    ncursor.execute("""SELECT count(*) from """+table)
    orow = ocursor.fetchone()
    nrow = ncursor.fetchone()
    if orow[0] != nrow[0]:
      print("%s->%s old:%s new:%s" % (db, table, orow[0], nrow[0]))

