
import iemdb, network, sys
asos = iemdb.connect('coop', bypass=True)
acursor = asos.cursor()
mesosite = iemdb.connect('mesosite')
mcursor = mesosite.cursor()

net = sys.argv[1]

table = network.Table( net )
ids = `tuple(table.sts.keys())`

acursor.execute("""SELECT station, min(day) from alldata_%s
  WHERE station in %s GROUP by station 
  ORDER by min ASC""" % (net[:2], ids))
for row in acursor:
    station = row[0]
    if table.sts[station]['archive_begin'] != row[1]:
        print 'Updated %s STS WAS: %s NOW: %s' % (station, 
                    table.sts[station]['archive_begin'], row[1])
  
    mcursor.execute("""UPDATE stations SET archive_begin = %s 
         WHERE id = %s and network = %s""" , (row[1], station, net) )
  
mcursor.close()
mesosite.commit()
mesosite.close()
