"""
Check to see if there are webcams offline, generate emails and such
"""

import os
import mx.DateTime
import stat
import tracker
track = tracker.Engine()
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()
now = mx.DateTime.now()

# Determine sites offline
offline = {}
icursor.execute("""SELECT station, valid from offline 
    WHERE network IN ('KCCI','KELO','KCRG', 'KCWI')""")
for row in icursor:
    offline[ row[0] ] = row[1]

# Now lets check files
mydir = "/home/ldm/data/camera/stills"
files = os.listdir(mydir)

mcursor.execute("""
    SELECT id, network, name from webcams where 
    network in ('KELO','KCCI','KCRG', 'KCWI')
    and online ORDER by id ASC
""")

emails = 0
for row in mcursor:
    fn = "%s/%s.jpg" % (mydir, row[0])
    if not os.path.isfile(fn):
        print 'Missing webcam file: %s' % (fn,)
        continue

    mtime = os.stat(fn)[stat.ST_MTIME]
    ts = mx.DateTime.DateTimeFromTicks(mtime)
    age = float(now) - mtime
    network = row[1]
    portfolio = "%ssnet" % (network.lower(),)

    if age > 3600 and not offline.has_key(row[0]):
        emails += 1
        track.doAlert(row[0], {'ts': ts, 'sname': row[2] +' Webcam'}, 
                      network, portfolio, False)
    elif age < 3600 and offline.has_key(row[0]):
        emails += 1
        track.checkStation(row[0], {'ts': ts, 'sname': row[2] +' Webcam'}, 
                           network, portfolio, False)
        
if emails < 5:
    track.send()
else:
    print 'Skipping check_webcams email due to too many emails'
    
# done