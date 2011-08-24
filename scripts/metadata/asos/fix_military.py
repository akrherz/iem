# Need to fix the station table mess I have for KQ?? sites

import iemdb
IEM = iemdb.connect('iem')
MESOSITE = iemdb.connect('mesosite')
icursor = IEM.cursor()
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

# Load up all my Q?? IQ_ASOS sites
mcursor.execute("""
 SELECT id, name from stations where network = 'IQ_ASOS'
 and substring(id,0,2) = 'Q'
 """)
for row in mcursor:
 kid = 'K%s' % (row[0],)
 mcursor2.execute("""SELECT * from stations where
  id = %s""", (kid,))
 if mcursor2.rowcount == 1:
   print 'Found', kid
   mcursor2.execute("""DELETE from stations where network = 'IQ_ASOS'
   and id = %s""", (row[0],))
   mcursor2.execute("""UPDATE stations SET id = %s WHERE id = %s""", 
    (row[0], kid))

mcursor2.close()
MESOSITE.commit()
  
