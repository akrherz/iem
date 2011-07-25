"""
Dump a day's worth of METAR data out and generate a 
GEMPAK surface file, hopefully!
"""
import mx.DateTime
import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
acursor.execute("SET TIME ZONE 'GMT'")
import os, sys

def run(ts):
    output = open("%s.metar" % (ts.strftime("%Y%m%d"),), 'w')

    acursor.execute("""
    SELECT metar, valid from t%s WHERE valid BETWEEN '%s 00:00+00' and '%s 23:59+00' and 
    metar is not null and metar != '' ORDER by valid ASC
   """ % (ts.year, ts.strftime("%Y-%m-%d"), ts.strftime("%Y-%m-%d")))
    oldhr = 23
    for row in acursor:
        if row[1].hour != oldhr:
            output.write('\003\001\r\r\n000\r\r\n') 
            output.write("SAUS70 KXXX %02i%02i59\r\r\n" % (ts.day, row[1].hour))
            output.write("METAR\r\r\n")
            oldhr = row[1].hour
        output.write("%s=\r\r\n" % (row[0].replace("METAR ", ""),))
    output.write('\003')
    output.close()
    
    cmd = "cat %s.metar | dcmetr -v 8 -c %s/0000 -b 24 -d %s.log -s /mesonet/TABLES/azos.stns -m 72 %s.gem" % (
                    ts.strftime("%Y%m%d"), (ts + mx.DateTime.RelativeDateTime(days=1)).strftime("%Y%m%d"),
                    ts.strftime("%Y%m%d"),  ts.strftime("%Y%m%d"))
    os.system( cmd )
    
    # GEMPAK plotting time!
    for hr in range(0,24):
        now = ts + mx.DateTime.RelativeDateTime(hours=hr)
        cmd = "csh MW_mesonet.csh %s" % (now.strftime("%Y %m %d %H"),)
        os.system( cmd )
    
if __name__ == '__main__':
    run( mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))