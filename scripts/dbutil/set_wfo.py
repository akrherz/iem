"""
 Assign a WFO to sites in the metadata tables that have no WFO set
$Id: $:
"""

import re
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

# Find sites we need to check on
mcursor.execute("""select s.id, c.wfo, s.iemid, s.network 
  from stations s, cwa c WHERE 
  s.geom && c.the_geom and contains(c.the_geom, s.geom) 
  and (s.wfo IS NULL or s.wfo = '') and s.country = 'US' """)

for row in mcursor:
  id = row[0]
  wfo = row[1]
  iemid = row[2]
  network = row[3]
  if wfo is not None:
    print 'Assinging WFO: %s to IEMID: %s ID: %s NETWORK: %s' % (wfo,
     iemid, id, network)
    mcursor2.execute("UPDATE stations SET wfo = '%s' WHERE iemid = %s" % (
         wfo, iemid) )
  else:
    print 'ERROR assigning WFO to IEMID: %s ID: %s NETWORK: %s' % (
     iemid, id, network)


mcursor.close()
mcursor2.close()
MESOSITE.commit()
MESOSITE.close()
