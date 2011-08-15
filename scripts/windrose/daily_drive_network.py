# We are going to process one network per day every day!
import iemdb, os, sys
import stat
import mx.DateTime
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
now = mx.DateTime.now()

mcursor.execute("""SELECT max(id), network from stations 
    WHERE network ~* 'ASOS' GROUP by network""")
for row in mcursor:
    network = row[1]
    testfp = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (row[0],)
    if not os.path.isfile(testfp):
        os.system("/mesonet/python/bin/python drive_network_windrose.py %s" % (network,))
        sys.exit()
    else:
        mtime = os.stat(testfp)[stat.ST_MTIME]
        age = float(now) - mtime
        if age > (50*24*60): #50 days
            os.system("/mesonet/python/bin/python drive_network_windrose.py %s" % (network,))
            sys.exit()