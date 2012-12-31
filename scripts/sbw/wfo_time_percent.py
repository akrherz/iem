import iemdb
import numpy
import network

nt = network.Table("WFO")

POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

import mx.DateTime

sts = mx.DateTime.DateTime(2005,10,1)
ets = mx.DateTime.DateTime(2013,1,1)
interval = mx.DateTime.RelativeDateTime(hours=3)

bins = (ets - sts).minutes

for wfo in nt.sts.keys():
    wfo = wfo[-3:]
    counts = numpy.zeros( (int(bins)), 'f')

    pcursor.execute("""SELECT distinct issue, expire from warnings where wfo = '%s'
        and issue > '2005-10-01' and expire < '2013-01-01' and gtype = 'C'
        and phenomena = 'SC' """ % (wfo,))
    
    for row in pcursor:
        issue = mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")    
        expire = mx.DateTime.strptime(row[1].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
        
        idx1 = int((issue - sts).minutes)
        idx2 = int((expire - sts).minutes)
        counts[idx1:idx2] = 1
        
    print "%s,%.4f" % (wfo, numpy.sum( counts ) / float(bins))
    
    pcursor.execute("""INSERT into ferree3(wfo, percentage) values (%s,%s)""",
                    (wfo, float(numpy.sum( counts ) / float(bins))))
    POSTGIS.commit()
    
pcursor.close()
POSTGIS.commit()
POSTGIS.close()