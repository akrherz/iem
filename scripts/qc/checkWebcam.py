
from pyIEM import iemAccess, tracker, cameras
import os, mx.DateTime, stat

iemaccess = iemAccess.iemAccess()
now = mx.DateTime.now()

# Determine sites offline
offline = {}
rs = iemaccess.query("SELECT * from offline WHERE network IN ('KCCI','KELO','KCRG')").dictresult()
for i in range(len(rs)):
    offline[ rs[i]['station'] ] = rs[i]['valid']

class fakest:
    def __init__(self,):
        self.sts = {}

class fakeOb:
    def __init__(self,):
        self.ts = None

# Now lets check files
dir = "/home/ldm/data/camera/stills/"
files = os.listdir(dir)
network = "KCCI"
for file in files:
    if (file == "SMAI4.jpg" or file == "S03I4.jpg" or file == "KCRG-014.jpg"):
        continue
    if len(file) > 4 and file[:4] == "IDOT":
        continue
    fp = "%s/%s" % (dir, file)
    mtime = os.stat(fp)[stat.ST_MTIME]
    age = float(now) - mtime
    if (len(file) > 10):
      id = "%s" % (file.split(".")[0],)
      network = file[:4]
    else:
      id = "W%s" % (file[:4],)
    nwsli = file.split(".")[0]
    st = fakest()
    st.sts[ id ] = {'name': cameras.cams[nwsli]['name'] + " Webcamera"}
    myOb = fakeOb()
    myOb.ts = mx.DateTime.DateTimeFromTicks( mtime )
    if (age > 3600 and not offline.has_key(id)):
        #print "ALERT!", file
        tracker.doAlert(st, id, myOb, network, network.lower() +'snet' , 0)
    elif (age < 3600 and offline.has_key(id)):
        #print "BACK ONLINE!", file
        tracker.checkStation(st, id, myOb, network, network.lower() +'snet', 0)
