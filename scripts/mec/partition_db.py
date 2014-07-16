import psycopg2

def do(unitnumber, tid):
  pgconn = psycopg2.connect(database='mec', host='192.168.0.23')
  cursor = pgconn.cursor()
  cursor.execute("""SET work_mem='8GB'""")

  #cursor.execute("""CREATE INDEX turbine_data_%s_valid_idx
  # on turbine_data_%s(valid)""" % (unitnumber, unitnumber))

  cursor.execute("""
  UPDATE turbine_data_%s  SET yaw = null where yaw < 0
  """ % (unitnumber,))
  print 'yaw bad: %s' % (cursor.rowcount,)
  cursor.execute("""
  UPDATE turbine_data_%s  SET windspeed = null where windspeed < 0
  """ % (unitnumber,))
  print 'wind speed bad: %s' % (cursor.rowcount,)


  cursor.close()
  pgconn.commit()
  pgconn.close()


pgconn2 = psycopg2.connect(database='mec', host='192.168.0.23')
cursor2 = pgconn2.cursor()

cursor2.execute("""select unitnumber, id from turbines""")
for row in cursor2:
  print 'Run %s %s' % (row[0], row[1])
  do(row[0], row[1])
