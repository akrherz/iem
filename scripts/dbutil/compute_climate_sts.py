'''
 Determine when a CLIMATE track site started...
'''
import psycopg2
import network
import sys
asos = psycopg2.connect(database='coop', host='iemdb')
acursor = asos.cursor()
mesosite = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = mesosite.cursor()

net = sys.argv[1]

nt = network.Table( net )

acursor.execute("""SELECT station, min(day) from alldata_%s GROUP by station 
  ORDER by min ASC""" % (net[:2]))
for row in acursor:
    station = row[0]
    if not nt.sts.has_key(station):
        continue
    if nt.sts[station]['archive_begin'] != row[1]:
        print 'Updated %s STS WAS: %s NOW: %s' % (station, 
                    nt.sts[station]['archive_begin'], row[1])
  
    mcursor.execute("""UPDATE stations SET archive_begin = %s 
         WHERE id = %s and network = %s""" , (row[1], station, net) )
  
mcursor.close()
mesosite.commit()
mesosite.close()
