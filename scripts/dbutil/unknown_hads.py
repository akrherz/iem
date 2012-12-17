"""
 I look at the unknown HADS table and see if any of these stations exist
 in the mesosite database, if so, then I set online to true!
"""

import iemdb

HADS = iemdb.connect('hads')
MESOSITE = iemdb.connect('mesosite')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()
mcursor = MESOSITE.cursor()

# look for unknown
hcursor.execute("""SELECT distinct nwsli, network from unknown 
    WHERE network != '' and network is not null""")
for row in hcursor:
    nwsli = row[0]
    network = row[1]
    mcursor.execute("""
  SELECT online from stations where network = '%s' and id = '%s'
      """ % (network, nwsli))
    row = mcursor.fetchone()
    if row is None:
        continue
    elif row[0] == False:
        print 'Site %s [%s] was unknown, but is in mesosite' % (nwsli, network)
        mcursor.execute(""" 
          update stations SET online = 't' where network = '%s' and id = '%s'
        """ % (network, nwsli))
        hcursor2.execute("""DELETE from unknown where nwsli = '%s' and network = '%s'""" % (
                                                            nwsli, network))
    else:
        print 'Site %s [%s] was unknown, but online in DB?' % (nwsli, network)
        hcursor2.execute("""DELETE from unknown where nwsli = '%s' and network = '%s'""" % (
                                                    nwsli, network))
 
hcursor2.close()
HADS.commit()
mcursor.close()
MESOSITE.commit()
