# Need something to fix the daily precip values.  (Ingestor bug perhaps)

# Steps
#  Sample last 10 lines of data archive file
#  Pick highest value and set pday equal to that

from pyIEM import mesonet, iemAccessDatabase
import mx.DateTime, sys, os


iemaccess = iemAccessDatabase.iemAccessDatabase()

def process(ts):
    for id in mesonet.snetConv.keys():
        nwsli = mesonet.snetConv[id]
        #
        fp = "/mesonet/ARCHIVE/raw/snet/%s/%s.dat" % (ts.strftime("%Y_%m/%d"), id)
        if (not os.path.isfile(fp)):
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

        sql = "UPDATE summary_%s SET pday = %s WHERE station = '%s' and day = '%s' " % (ts.year, maxPrecip, nwsli, ts.strftime("%Y-%m-%d") )
        iemaccess.query(sql)



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
