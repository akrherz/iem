"""
We need to look at the raw SNET datafiles and see what the daily precip should
have been.  Due to complex issues with clocks, we should see the largest 
value in the raw data file and use that for the daily precip value stored in
the summary database

Runs from: RUN_MIDNIGHT.sh

"""
import iemdb
IEM = iemdb.connect('iem')
icursor = IEM.cursor()
from pyIEM import mesonet
import mx.DateTime
import sys
import os
import network
nt = network.Table(["KCCI","KIMT","KELO"])

def process(ts):
    for nwsli in nt.sts.keys():
        nwnid = nt.sts[nwsli]['nwn_id']
        #
        fp = "/mesonet/ARCHIVE/raw/snet/%s/%s.dat" % (ts.strftime("%Y_%m/%d"), 
                                                      nwnid)
        if not os.path.isfile(fp):
            #print 'Missing: %s' % (fp,)
            continue

        maxPrecip = -99
        lines = open(fp).readlines()
        for line in lines[-10:]:
            tokens = line.split(",")
            pDay = float(tokens[9][:-2])
            if (pDay > maxPrecip):
                maxPrecip = pDay
  
        if (maxPrecip < 0):
            continue

        sql = """UPDATE summary_%s s SET pday = %s FROM stations t 
            WHERE t.id = '%s' and t.iemid = s.iemid 
            and day = '%s' """ % (ts.year, maxPrecip, nwsli, 
                                  ts.strftime("%Y-%m-%d") )
        icursor.execute(sql)

ts = mx.DateTime.now() - mx.DateTime.RelativeDateTime(days=1)
if (len(sys.argv) == 4):
    ts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
process(ts)
"""
sts = mx.DateTime.DateTime(2004,1,1)
ets = mx.DateTime.DateTime(2005,7,25)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
while now < ets:
    print now
    process(now)
    now += interval
"""
icursor.close()
IEM.commit()