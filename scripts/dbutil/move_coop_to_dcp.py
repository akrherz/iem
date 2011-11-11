import iemdb
IEM = iemdb.connect('iem')
icursor = IEM.cursor()
icursor2 = IEM.cursor()
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

# Look for over-reporting COOPs
icursor.execute("""
 select id, network, count(*), max(raw) from current_log c JOIN stations s ON (s.iemid = c.iemid)
 where network ~* 'COOP' and valid > '2011-11-10' 
 GROUP by id, network ORDER by count DESC
""")
for row in icursor:
  id = row[0]
  network = row[1]
  if row[2] < 5:
    continue
  # Look for how many entries are in mesosite
  mcursor.execute("""
  SELECT count(*) from stations where id = %s
  """, (id,))
  row = mcursor.fetchone()
  if row[0] == 1: # Switch candidate!
    newnetwork = network.replace("_COOP", "_DCP")
    print 'We shall switch %s from %s to %s' % (id, network, newnetwork)
    mcursor2.execute("""UPDATE stations SET network = '%s' WHERE id = '%s' 
   """ % (newnetwork, id))

IEM.commit()
icursor2.close()
MESOSITE.commit()
mcursor.close()
