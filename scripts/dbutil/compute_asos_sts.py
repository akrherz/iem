"""
 Look into the ASOS database and figure out the start time of various 
 sites for a given network.
"""

import iemdb
import network
import sys
import datetime
import pytz

basets = datetime.datetime.now()
basets = basets.replace(tzinfo=pytz.timezone("America/Chicago"))

asos = iemdb.connect('asos', bypass=True)
acursor = asos.cursor()
mesosite = iemdb.connect('mesosite')
mcursor = mesosite.cursor()

net = sys.argv[1]

table = network.Table( net )
keys = table.sts.keys()
if len(keys) > 1:
    ids = `tuple(keys)`
else:
    ids = "('%s')" % (keys[0],)

acursor.execute("""SELECT station, min(valid), max(valid) from alldata 
  WHERE station in %s GROUP by station 
  ORDER by min ASC""" % (ids,))
for row in acursor:
    station = row[0]
    if table.sts[station]['archive_begin'] != row[1]:
        print 'Updated %s STS WAS: %s NOW: %s' % (station, 
                    table.sts[station]['archive_begin'], row[1])
  
    mcursor.execute("""UPDATE stations SET archive_begin = %s 
         WHERE id = %s and network = %s""" , (row[1], station, net) )
    if mcursor.rowcount == 0:
        print 'ERROR: No rows updated'
  
    # Site without data in past year is offline!
    if (basets - row[2]).days  > 365:
        if table.sts[station]['archive_end'] != row[2]:
            print 'Updated %s ETS WAS: %s NOW: %s' % (station, 
                    table.sts[station]['archive_end'], row[2])
  
            mcursor.execute("""UPDATE stations SET archive_end = %s 
                 WHERE id = %s and network = %s""" , (row[2], station, net) )
    # If it was offline and now is on, correct this
    if ((basets - row[2]).days  < 365 and 
        table.sts[station]['archive_end'] is not None):
        print 'Updated %s ETS WAS: %s NOW: None' % (station, 
                    table.sts[station]['archive_end'])
  
        mcursor.execute("""UPDATE stations SET archive_end = null 
                 WHERE id = %s and network = %s""" , ( station, net) )
    
mcursor.close()
mesosite.commit()
mesosite.close()
