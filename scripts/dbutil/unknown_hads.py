import iemdb
import os

HADS = iemdb.connect('hads')
MESOSITE = iemdb.connect('mesosite')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()
mcursor = MESOSITE.cursor()

# look for unknown
hcursor.execute("SELECT distinct nwsli, network from unknown WHERE network != '' and network is not null")
for row in hcursor:
  id = row[0]
  network = row[1]
  mcursor.execute("""
  SELECT * from stations where network = '%s' and id = '%s'
  """ % (network, id))
  row = mcursor.fetchone()
  if row:
    #mcursor.execute("""
    #  update stations SET online = 't' where network = '%s' and id = '%s'
    #""" % (network, id))
    os.system("python addSiteMesosite.py %s %s" % (network, id))
    hcursor2.execute("""DELETE from unknown where nwsli = '%s' and network = '%s'""" % (id, network))
  else:
    pass
    #print 'Unknown %s %s' % (network, id)

hcursor2.close()
HADS.commit()
mcursor.close()
MESOSITE.commit()
