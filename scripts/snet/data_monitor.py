#  Process that would continually monitor for interesting stuff!!
# Daryl Herzmann 19 Aug 2002
# 27 Aug 2002:	Use a more efficient Array restacker...
# 31 May 2005	Use iemaccess...

#  File Template  site.event.duration

from pyIEM import stationTable, iemAccess, sob
#iemaccess = iemAccess.iemAccess()
import os, time, sys, pg
st = stationTable.stationTable("/mesonet/TABLES/snet.stns")

o = open('data_monitor.pid', 'w')
o.write("%s" % (os.getpid(),))
o.close()

db = {}
for station in st.ids:
  db[station] = {"pday": [0]*60 }

# Load up arrays for the first time....
def preload():
    iemaccess = pg.connect("iem", 'iemdb')
    sql = "SELECT pday, station from current WHERE \
      network in ('KCCI','KELO','KIMT')"
    rs = iemaccess.query(sql).dictresult()
    for i in range(len(rs)):
        sid = rs[i]['station']

        db[sid]["pday"] = [rs[i]['pday']]*60
    iemaccess.close()

def process(tv):
# (station varchar(10), network varchar(10), valid timestamp with time zone, event varchar(10), magnitude real
    iemaccess = pg.connect("iem", 'iemdb')
    sql = "SELECT pday, station from current WHERE \
      network = '%s'" % (tv,)
    rs = iemaccess.query(sql).dictresult()
    for i in range(len(rs)):
        sid = rs[i]['station']
        pday = rs[i]['pday']
        db[sid]["pday"] = [pday] + db[sid]["pday"][0:-1]

        oldTMPF = db[sid]["pday"][14]
        if ( oldTMPF < pday ):
            accum = pday - float(db[sid]["pday"][14])
            #fileRef = "%s.%s.%s" % (sid, "P+", "1min")
            #o = open("/mesonet/share/"+tv+"_events/"+ fileRef, "w")
            #o.write( str(accum) )
            #o.close()
            sql = "DELETE from events WHERE station = '%s' and network = '%s'\
                   and event = 'P+'" % (sid, tv)
            iemaccess.query(sql)
            sql = "INSERT into events (station, network, valid, event, magnitude) VALUES ('%s','%s',now(), 'P+', %s)" % (sid, tv, accum)
            iemaccess.query(sql)

        d = pday - float(db[sid]["pday"][59])
        if (d < 0):
          d = pday
        sql = "UPDATE current SET phour = %s WHERE station = '%s' " % (d, sid)
        #print sql
        iemaccess.query(sql)
    iemaccess.close()

def Main():
    preload()
    while (1):
        try:
            process('KCCI')
            process('KELO')
            process('KIMT')
        except:
            v, i, o = sys.exc_info()
            print "%s\n" % (sys.excepthook(v, i, o),) 
            sys.exit()
        time.sleep(60)

Main()
