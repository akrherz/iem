"""
 Figure out when the RWIS data started...
"""

import psycopg2
import network
import sys
import datetime
import pytz

basets = datetime.datetime.now()
basets = basets.replace(tzinfo=pytz.timezone("America/Chicago"))

rwis = psycopg2.connect(database='rwis', host='iemdb')
rcursor = rwis.cursor()
mesosite = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = mesosite.cursor()

network = sys.argv[1]
table = network.Table(network)

rcursor.execute("""SELECT station, min(valid), max(valid) from alldata 
    GROUP by station ORDER by min ASC""")
for row in rcursor:
    station = row[0]
    if not table.sts.has_key(station):
        continue
    if table.sts[station]['archive_begin'] != row[1]:
        print 'Updated %s STS WAS: %s NOW: %s' % (station, 
                    table.sts[station]['archive_begin'], row[1])
  
    mcursor.execute("""UPDATE stations SET archive_begin = %s 
         WHERE id = %s and network = %s""" , (row[1], station, network) )
    if mcursor.rowcount == 0:
        print 'ERROR: No rows updated'
    
mcursor.close()
mesosite.commit()
mesosite.close()
