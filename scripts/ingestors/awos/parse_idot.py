
import re, sys, mx.DateTime, os
from pyIEM import  awosOb, iemAccessOb, iemAccess, stationTable, tracker
from twisted.python import log

log.startLogging( open('/tmp/parse_idot.log', 'a') )

threshold = mx.DateTime.RelativeDateTime(minutes=45)

iemaccess = iemAccess.iemAccess()
st = stationTable.stationTable("/mesonet/TABLES/awos.stns")

o = open("/mesonet/data/incoming/AWOS.DAT",'r').readlines()
cdf = open("awos.csv","w")

gmt_now = mx.DateTime.gmt()
sDate = gmt_now.strftime("%d%H%M")

collectfp = "awos%s.dat" % (sDate,)
collect = open(collectfp, "w")

collect.write("\001\015\015\012001\n")
collect.write("SAUS70 KISU "+sDate+"\015\015\012")
collect.write("METAR\015\015\012")

def dontEmail(network):
    cnt_offline = 0
    # First, look into the offline database to see how many active tickets
    rs = iemaccess.query("SELECT count(*) as c from offline WHERE \
      network = '%s'" % (network,) ).dictresult()
    if (len(rs) > 0):
        cnt_offline = rs[0]['c']
        log.msg("Portfolio #offline: %s " % (cnt_offline,) )

    if (cnt_offline > 10):
        return 1

    # Okay, pre-emptive check to iemdb to see how many obs are old
    lastts = mx.DateTime.now() - threshold
    rs = iemaccess.query("SELECT count(*) as c from current WHERE \
      network = '%s' and valid < '%s' " % \
      (network, lastts.strftime('%Y-%m-%d %H:%M') ) ).dictresult()
    if (len(rs) > 0):
        cnt_offline = rs[0]['c']
        log.msg("IEMAccess says #offline: %s" % (cnt_offline,) )
    if (cnt_offline > 10):
        return 1

    return 0


dontmail = dontEmail('AWOS')
obs = []
cnt_offline = 0
for i in range(len(o)):
  thisLine = re.sub(",", "", o[i])
  myOb = awosOb.awosOb(thisLine)
  if (myOb.error > 0):
    log.msg("myOb.error: %s, :%s:" % (myOb.error, thisLine) ) 
    continue
  if ((myOb.gmt_ts - gmt_now).days > 10):
    log.msg("myOb future ts: %s %s" % (myOb.faaID, myOb.gmt_ts ) ) 
    continue

  obs.append(myOb)
  floor = gmt_now - threshold
  if ( myOb.gmt_ts < floor ):
    cnt_offline += 1

if (cnt_offline > 10):
  dontmail = 1

log.msg("Recheck: dontmail: %s, cnt_offline: %s" % (dontmail, cnt_offline) )

for myOb in obs:
  floor = gmt_now - threshold
  if ( myOb.gmt_ts < floor ):
    tracker.doAlert(st, myOb.faaID, myOb, "AWOS", "iaawos", dontmail)
    continue

  tracker.checkStation(st, myOb.faaID, myOb, "AWOS", "iaawos", dontmail)
  # First do the normal Ones
  if (myOb.error == 0):
    try:
      myOb.calc()
    except:
      log.write( thisLine +"\n")
      log.err()
      continue
    myOb.printMetar(collect, "")

  myOb.printCDF(cdf)
  #fRef = open("/mesonet/data/current/awos/"+ myOb.faaID +".dat", "w")
  #myOb.printCDF(fRef)
  #fRef.close()

  #mRef = open("METAR/METAR_K"+ myOb.faaID, "w")
  #myOb.printMetar(mRef, "")
  #mRef.close()

  iemob = iemAccessOb.iemAccessOb( myOb.faaID , 'AWOS')
  iemob.setObTimeGMT( myOb.gmt_ts )
  iemob.load_and_compare(iemaccess.iemdb)
  if (myOb.tmpf != None):
    iemob.data['tmpf'] = myOb.tmpf
  if (myOb.dwpf != None):
    iemob.data['dwpf'] = myOb.dwpf
  if (myOb.sknt != None):
    iemob.data['sknt'] = myOb.sknt
  if (myOb.drct != None):
    iemob.data['drct'] = myOb.drct
  if (myOb.gust != None):
    iemob.data['gust'] = myOb.gust
  if (myOb.vsby != None):
    iemob.data['vsby'] = myOb.vsby
  if (myOb.alti != None):
    iemob.data['alti'] = myOb.alti
  if (myOb.p01i != None):
    iemob.data['phour'] = myOb.p01i
  iemob.updateDatabase(iemaccess.iemdb)
  del(iemob)

# Away with our fake METAR
collect.close()
si, se = os.popen4("/home/ldm/bin/pqinsert %s" % (collectfp,) )
os.unlink( collectfp )

# Away with our CSV
cdf.close()
si, se = os.popen4("/home/ldm/bin/pqinsert -p 'plot c 000000000000 csv/awos.csv bogus csv' awos.csv")
os.unlink("awos.csv")
