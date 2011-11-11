"""
Need something to set the time zone of networks
"""
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

mcursor.execute("""
 SELECT id, name from networks where tzname is null
""")

for row in mcursor:
  id = row[0]
  name = row[1]

  mcursor2.execute("""SELECT tzname, count(*) from stations where network = '%s' and tzname is not null GROUP by tzname ORDER by count DESC
  """ % (id,))
  row2 = mcursor2.fetchone()
  if row2 == None or row2[0] == 'uninhabited':
    print '--> MISSING ID: %s' % (id, )
  else:
    print 'ID: %s TIMEZONE: %s' % (id, row2[0])
    mcursor2.execute("UPDATE networks SET tzname = '%s' WHERE id = '%s' " % (row2[0], id ))

mcursor2.close()
MESOSITE.commit()
