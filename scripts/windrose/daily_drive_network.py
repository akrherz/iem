# We are going to process one network per day every day!
import iemdb, os, sys
import stat
import mx.DateTime
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
now = mx.DateTime.now()

mcursor.execute("""SELECT max(id), network from stations 
    WHERE network ~* 'ASOS' and online = 't' and country = 'US' 
    GROUP by network ORDER by random()""")
for row in mcursor:
    network = row[1]
    testfp = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (row[0],)
    if not os.path.isfile(testfp):
        print "Driving network %s because no file" % (network,)
        os.system("/mesonet/python/bin/python drive_network_windrose.py %s" % (network,))
        sys.exit()
    else:
        mtime = os.stat(testfp)[stat.ST_MTIME]
        age = float(now) - mtime
        if age > (50*24*60*60): #50 days in seconds!
            print "Driving network %s because of age!" % (network,)
            os.system("/mesonet/python/bin/python drive_network_windrose.py %s" % (network,))
            sys.exit()