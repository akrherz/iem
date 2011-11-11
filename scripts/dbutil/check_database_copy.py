import psycopg2

tables = """SELECT relname  FROM pg_class C
  LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
  WHERE nspname NOT IN ('pg_catalog', 'information_schema')  and nspname = 'public' and relkind = 'r'
"""

data = {'192.168.0.19': {}, 'iem20': {} }

for host in data.keys():
  dbconn = psycopg2.connect('dbname=mesonet host='+host)
  cursor = dbconn.cursor()
  cursor.execute("select datname from pg_database where datname not in ('template1','template0')")
  for row in cursor:
     data[host][row[0]] = {}
     dbconn2 = psycopg2.connect('dbname='+row[0]+' host='+ host)
     cursor2 = dbconn2.cursor()
     cursor2.execute(tables)
     for row2 in cursor2:
        data[host][row[0]][row2[0]] = -1
     for tbl in data[host][row[0]].keys():
       cursor2.execute("SELECT count(*) from %s" % (tbl,))
       row2 = cursor2.fetchone()
       data[host][row[0]][tbl] = row2[0]
       print 'HOST: %16s DB: %16s TBL: %16s CNT: %14d' % (host, row[0], tbl, row2[0])
     dbconn2.close()

print '---------------------'
for db in data['iem20'].keys():
   for tbl in data['iem20'][db].keys():
     print '%s %s iem20: %14d  iem19: %14d  %6d' % (db, tbl, data['iem20'][db][tbl],
         data['192.168.0.19'][db][tbl], data['192.168.0.19'][db][tbl] - data['iem20'][db][tbl])

