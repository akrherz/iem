"""
Need something to check over the ASOS / AWOS temperatures, find trouble makers
"""

import psycopg2
import numpy as np
import datetime
IEM = psycopg2.connect(database="iem", host='iemdb', user='nobody')
icursor = IEM.cursor()

def checkdate(ts):
    '''
    check a date's worth of data for troublemakers
    '''
    strdate = ts.strftime("%Y-%m-%d")
    icursor.execute("""SELECT t.id, max_tmpf, min_tmpf 
    from summary s JOIN stations t ON (t.iemid = s.iemid)
    WHERE day = %s and t.network in ('IA_ASOS','AWOS')
    and max_tmpf > min_tmpf""", (strdate,))
                                    
    highs = []
    lows = []
    stations = []
    for row in icursor:
        stations.append(row[0])
        highs.append(row[1])
        lows.append(row[2])
        
    highs = np.array(highs)
    lows = np.array(lows)
    # Check 1: Look for largish differences between high and low
    meandelta = np.average(highs-lows)

    for sid in np.where( (highs-lows)>(meandelta*1.5), stations, None):
        if sid is not None:
            idx = stations.index(sid)
            print 'Delta   %s %s %5.1f %5.1f Tolerance: %5.1f' % (sid,
                                 strdate, highs[idx], lows[idx], meandelta*1.5)
    # Check 2: Two sigma temperatures
    thres1 = np.average(highs) + (np.std(highs) * 2.)
    thres2 = np.average(highs) - (np.std(highs) * 2.)
    for sid in np.where( highs > thres1, stations, None):
        if sid is not None:
            idx = stations.index(sid)
            print '+2sigma %s %s %5.1f %5.1f Tolerance: %5.1f %5.1f' % (sid,
                        strdate, highs[idx], lows[idx], thres1, thres2)                 
    for sid in np.where( highs < thres2, stations, None):
        if sid is not None:
            idx = stations.index(sid)
            print '-2sigma %s %s %5.1f %5.1f Tolerance: %5.1f %5.1f' % (sid,
                                strdate, highs[idx], lows[idx], thres1, thres2)                 
    
if __name__ == "__main__":
    for i in range(0,2):
        checkdate( datetime.datetime.now() - datetime.timedelta(days=i))
