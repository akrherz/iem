"""
  Process that would continually monitor for interesting stuff!!
"""
from pyiem.network import Table as NetworkTable
import psycopg2
import os
import sys
import time
nt = NetworkTable(("KCCI", "KIMT", "KELO"))

# Write PID
o = open('data_monitor.pid', 'w')
o.write("%s" % (os.getpid(),))
o.close()

db = {}
for station in nt.sts.keys():
    db[station] = {"pday": [0]*60}


def preload():
    IEM = psycopg2.connect(database='iem', host='iemdb')
    icursor = IEM.cursor()
    icursor.execute("""SELECT pday, t.id from current c, stations t WHERE
      t.network in ('KCCI','KELO','KIMT') and c.iemid = t.iemid
      and pday is not null""")
    for row in icursor:
        sid = row[1]
        db[sid]["pday"] = [row[0]]*60
    IEM.close()


def process(tv):
    """Process a given network of stations"""
    IEM = psycopg2.connect(database='iem', host='iemdb')
    icursor = IEM.cursor()
    icursor2 = IEM.cursor()
    icursor.execute("""SELECT pday, t.id, t.iemid, phour
        from current c JOIN stations t on (c.iemid = t.iemid)
        WHERE t.network = '%s' and pday is not null""" % (tv,))
    for row in icursor:
        sid = row[1]
        pday = row[0]
        phour = row[3]
        db[sid]["pday"] = [pday] + db[sid]["pday"][0:-1]

        oldTMPF = db[sid]["pday"][14]
        if oldTMPF < pday:
            accum = pday - float(db[sid]["pday"][14])
            # fileRef = "%s.%s.%s" % (sid, "P+", "1min")
            # o = open("/mesonet/share/"+tv+"_events/"+ fileRef, "w")
            # o.write( str(accum) )
            # o.close()
            sql = """DELETE from events WHERE station = '%s' and network = '%s'
                   and event = 'P+'""" % (sid, tv)
            icursor2.execute(sql)
            sql = """INSERT into events (station, network, valid, event,
                magnitude) VALUES ('%s', '%s', now(), 'P+', %s)
                """ % (sid, tv, accum)
            icursor2.execute(sql)

        d = pday - float(db[sid]["pday"][59])
        if d < 0:
            d = pday
        if d != phour:
            icursor3 = IEM.cursor()
            icursor3.execute("""
                UPDATE current SET phour = %s WHERE iemid = %s
                """, (d, row[2]))
            icursor3.close()
            IEM.commit()
    icursor2.close()
    IEM.commit()
    IEM.close()


def main():
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

main()
