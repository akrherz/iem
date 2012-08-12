# We are going to process one network per day every day!
import iemdb
import os
import sys
import subprocess
import stat
import mx.DateTime
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
now = mx.DateTime.now()

mcursor.execute("""SELECT max(id), network from stations 
    WHERE (network ~* 'ASOS' or network = 'AWOS') 
    and online = 't' and country = 'US' 
    GROUP by network ORDER by random()""")
for row in mcursor:
    network = row[1]
    testfp = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (row[0],)
    if not os.path.isfile(testfp):
        print "Driving network %s because no file" % (network,)
        subprocess.call("python drive_network_windrose.py %s" % (network,),
                        shell=True)
        sys.exit()
    else:
        mtime = os.stat(testfp)[stat.ST_MTIME]
        age = float(now) - mtime
        # 55 days in seconds, enough to cover the number of networks running
        if age > (55*24*60*60): 
            print "Driving network %s because of age!" % (network,)
            subprocess.call("python drive_network_windrose.py %s" % (network,),
                            shell=True)
            sys.exit()
