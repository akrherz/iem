"""Search for a network to generate windroses for

Called from RUN_2AM.sh script
"""
import psycopg2
import os
import subprocess
import stat
import datetime

MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
CACHEDIR = "/mesonet/share/windrose/climate/yearly"


def do_network(network):
    """Process a network"""
    # Update the STS while we are at it, this will help the database get
    # stuff cached too
    subprocess.call("python ../dbutil/compute_asos_sts.py %s" % (network,),
                    shell=True)
    subprocess.call("python drive_network_windrose.py %s" % (network,),
                    shell=True)


def main():
    """Main"""
    mcursor = MESOSITE.cursor()
    now = datetime.datetime.now()
    mcursor.execute("""SELECT max(id), network from stations
        WHERE (network ~* 'ASOS' or network = 'AWOS')
        and online = 't' GROUP by network ORDER by random()""")
    for row in mcursor:
        network = row[1]
        testfn = "%s/%s_yearly.png" % (CACHEDIR, row[0])
        if not os.path.isfile(testfn):
            print "Driving network %s because no file" % (network,)
            do_network(network)
            return
        else:
            mtime = os.stat(testfn)[stat.ST_MTIME]
            age = float(now.strftime("%s")) - mtime
            # 250 days in seconds, enough to cover the number of networks
            if age > (250*24*60*60):
                print "Driving network %s because of age!" % (network,)
                do_network(network)
                return

if __name__ == '__main__':
    main()
