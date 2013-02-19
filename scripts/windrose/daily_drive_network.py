"""
 Run from the RUN_2AM.sh script, we randomly pick a ASOS network to generate
 long-term cached windroses of 
"""
import iemdb
import os
import sys
import subprocess
import stat
import datetime

MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
now = datetime.datetime.now()

mcursor.execute("""SELECT max(id), network from stations 
    WHERE (network ~* 'ASOS' or network = 'AWOS') 
    and online = 't' GROUP by network ORDER by random()""")
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
        age = float(now.strftime("%s")) - mtime
        # 250 days in seconds, enough to cover the number of networks running
        if age > (250*24*60*60): 
            print "Driving network %s because of age!" % (network,)
            subprocess.call("python drive_network_windrose.py %s" % (network,),
                            shell=True)
            sys.exit()
