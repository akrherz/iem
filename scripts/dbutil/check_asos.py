import iemdb
ASOS = iemdb.connect('asos')
acursor = ASOS.cursor()
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

# Find blank start stations!
mcursor.execute("""
select id, network from stations where archive_begin is null and network ~* 'ASOS' and online ORDER by network
""")
for row in mcursor:
  id = row[0]
  network = row[1]
  # Look in current for valid
  icursor.execute("""
  SELECT valid from current where station = %s and network = %s
  """, (id, network) )
  row = icursor.fetchone()
  if row:
    valid = row[0]
    if valid.year == 1980:
      print 'No current data for %s %s' % (id, network)
  else:
    mcursor2.execute(""" UPDATE stations SET online = 'f' where
    id = %s and network = %s """, (id, network) )
    print 'Setting %s %s to offline'  % (id, network)
    continue
  acursor.execute("""
   SELECT min(valid) from alldata where station = %s
  """, (id,))
  row = acursor.fetchone()
  print '%s %s IEMDB: %s ASOSDB: %s' % (id, network, valid, row[0])

MESOSITE.close()
