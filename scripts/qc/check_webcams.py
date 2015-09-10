"""
Check to see if there are webcams offline, generate emails and such
"""

import os
import datetime
import pytz
import stat
from pyiem.network import Table as NetworkTable
from pyiem.tracker import TrackerEngine
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb')
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
PORTFOLIO = psycopg2.connect(database='portfolio', host='iemdb')

# Now lets check files
mydir = "/home/ldm/data/camera/stills"
files = os.listdir(mydir)

threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
threshold = threshold.replace(tzinfo=pytz.timezone("UTC"))


def do(netname, pname):
    """Do something please"""
    mcursor = MESOSITE.cursor()
    mcursor.execute("""
        SELECT id, network, name from webcams where
        network = %s
        and online ORDER by id ASC
    """, (netname, ))
    NT = NetworkTable(None)
    obs = {}
    missing = 0
    for row in mcursor:
        NT.sts[row[0]] = dict(id=row[0], network=row[1], name=row[2],
                              tzname='America/Chicago')
        fn = "%s/%s.jpg" % (mydir, row[0])
        if not os.path.isfile(fn):
            missing += 1
            if missing > 1:
                print 'Missing webcam file: %s' % (fn,)
            continue
        ticks = os.stat(fn)[stat.ST_MTIME]
        valid = (datetime.datetime(1970, 1, 1) +
                 datetime.timedelta(seconds=ticks))
        valid = valid.replace(tzinfo=pytz.timezone("UTC"))
        obs[row[0]] = dict(valid=valid)
    # Abort out if no obs are found
    if len(obs) == 0:
        return

    tracker = TrackerEngine(IEM.cursor(), PORTFOLIO.cursor(), 10)
    tracker.process_network(obs, pname, NT, threshold)
    tracker.send_emails()
    IEM.commit()
    PORTFOLIO.commit()


for network in ['KCCI', 'KCRG', 'KELO', 'KCWI']:
    do(network, "%ssnet" % (network.lower(), ))
