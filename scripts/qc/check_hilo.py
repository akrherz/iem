"""
Need something to check over the ASOS / AWOS temperatures, find trouble makers
"""

import iemdb, numpy, datetime
IEM = iemdb.connect("iem", bypass=True)
icursor = IEM.cursor()

def checkdate(ts):
    '''
    check a date's worth of data for troublemakers
    '''
    strdate = ts.strftime("%Y-%m-%d")
    icursor.execute("""SELECT t.id, max_tmpf, min_tmpf from summary_"""+ `ts.year` +""" s JOIN stations t ON (t.iemid = s.iemid)
    WHERE day = %s and t.network in ('IA_ASOS','AWOS')
    and max_tmpf > min_tmpf""", (strdate,))
                                    
    highs = []
    lows = []
    stations = []
    for row in icursor:
        stations.append(row[0])
        highs.append(row[1])
        lows.append(row[2])
        
    highs = numpy.array(highs)
    lows = numpy.array(lows)
    # Check 1: Look for largish differences between high and low
    meandelta = numpy.average(highs-lows)

    for id in numpy.where( (highs-lows)>(meandelta*1.5), stations, None):
        if id is not None:
            idx = stations.index(id)
            print 'Delta   %s %s %5.1f %5.1f Tolerance: %5.1f' % (id,
                                 strdate   , highs[idx], lows[idx], meandelta*1.5)
    # Check 2: Two sigma temperatures
    thres1 = numpy.average(highs) + (numpy.std(highs) * 2.)
    thres2 = numpy.average(highs) - (numpy.std(highs) * 2.)
    for id in numpy.where( highs > thres1, stations, None):
        if id is not None:
            idx = stations.index(id)
            print '+2sigma %s %s %5.1f %5.1f Tolerance: %5.1f %5.1f' % (id,
                                  strdate,  highs[idx], lows[idx], thres1, thres2)                 
    for id in numpy.where( highs < thres2, stations, None):
        if id is not None:
            idx = stations.index(id)
            print '-2sigma %s %s %5.1f %5.1f Tolerance: %5.1f %5.1f' % (id,
                                  strdate,  highs[idx], lows[idx], thres1, thres2)                 
    
if __name__ == "__main__":
    for i in range(0,2):
        checkdate( datetime.datetime.now() - datetime.timedelta(days=i))
