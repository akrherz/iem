import iemdb
import iemtz
import datetime
import numpy
import network

nt = network.Table("WFO")

POSTGIS = iemdb.connect('postgis')
pcursor = POSTGIS.cursor()
pcursor.execute("SET TIME ZONE 'GMT'")

sts = datetime.datetime(2009,1,1)
sts = sts.replace(tzinfo=iemtz.UTC())
ets = datetime.datetime(2013,1,1)
ets = ets.replace(tzinfo=iemtz.UTC())




# One per minute
bins = (ets - sts).days * 1440 
totalbins = (ets - sts).days * 780

for wfo in nt.sts.keys():
    wfo = wfo[-3:]
    counts = numpy.zeros( (int(bins)), 'f')

    pcursor.execute("""select distinct begints, endts, endts - begints as diff from 
    vtec_events e JOIN vtec_ugc_log l on (l.vtec_event = e.id) 
    WHERE e.center = 'K%s' and endts > begints and begints > '2009-01-01 00:00+00' 
    and significance = 'Y' and phenomena in ('WI', 'FG', 'FL')
        """ % (wfo,))
#       and phenomena not in ('SV','TO','CF','FA','FF','FL','LS','BH', 'CF', 'GL',  'LO', 'LS',
#         'MA', 'MF', 'MS', 'MH', 'RP', 'SE', 'SU', 'SI','SW','SC','RB')
    #('BH', 'CF', 'GL',  'LO', 'LS', 
    #  'MA', 'MF', 'MS', 'MH', 'RP', 'SE', 'SU', 'SI','SW','SC','RB')
    #
    
    maxduration = 0
    for row in pcursor:
        diff = row[1] - row[0]
        duration = diff.days * 1440 + diff.seconds / 60.0
        if duration > maxduration:
            maxduration = duration
        
        idx1 = int((row[0] - sts).days * 1440 + (row[0] - sts).seconds / 60.0)
        idx2 = int((row[1] - sts).days * 1440 + (row[1] - sts).seconds / 60.0)
        counts[idx1:idx2] = 1
    
    # 9z each day to 22z (60*13 bins)
    running = 0
    for i in range(540, bins, 1440):
        running += numpy.sum( counts[i:i+780] )
    
    #totalbins = 0
    #running = 0
    #for yr in [2009,2010,2011]:
    #    october = datetime.datetime(yr,10,1)
    #    october = october.replace(tzinfo=iemtz.UTC())
    #    march = datetime.datetime(yr+1,4,1)
    #    march = march.replace(tzinfo=iemtz.UTC())
    #    offset1 = (october - sts).days * 1440.0
    #    offset2 = (march - sts).days * 1440.0
    #    totalbins += (offset2 - offset1)
    #    running += numpy.sum( counts[offset1:offset2] )
    
    #ratio = 0
    #for i in range(360, bins, 1440):
    #    if numpy.sum(counts[i:i+1440]) == 0:
    #        ratio += 1.0
    
    ratio = running / float(totalbins) * 100.
    print "%s,%.4f,%.4f,%.1f,%s" % (wfo, ratio, float(numpy.sum(counts)) / float(bins) * 100.0,
                            maxduration / 1440.0,  pcursor.rowcount)
    
    pcursor.execute("""INSERT into ferree3(wfo, percentage) values (%s,%s)""",
                    (wfo, float(ratio)))
    POSTGIS.commit()
    
pcursor.close()
POSTGIS.commit()
POSTGIS.close()
