"""
My purpose in life is to daily check the VTEC database and see if there are
any IDs that are missing.  daryl then follows up with the weather bureau
reporting anything he finds after an investigation.
"""
import mx.DateTime
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
pcursor2 = POSTGIS.cursor()

YEAR = mx.DateTime.now().year

def add_missing(wfo, phenomena, sig, eventid):
    """ Known knowns!"""
    pcursor2.execute("""INSERT into vtec_missing_events(year, wfo,
    phenomena, significance, eventid) VALUES (%s,%s,%s,%s,%s)""",
    (YEAR, wfo, phenomena, sig, eventid))

sql = """SELECT wfo, phenomena, significance, eventid from
  vtec_missing_events WHERE year = %s""" % (YEAR, )
pcursor.execute( sql )
missing = []
for row in pcursor:
    missing.append( '%s.%s.%s.%s' % (row[0], row[1], row[2], row[3]))

sql = """SELECT wfo, min(eventid), max(eventid), phenomena,
        significance from warnings_%s 
       WHERE phenomena IN ('MA','FF','SV','TO') and significance = 'W' 
       GROUP by wfo, phenomena, significance""" % (YEAR, )
pcursor.execute( sql )
for row in pcursor:
    sEvent = row[1]
    eEvent = row[2]
    phenomena = row[3]
    wfo = row[0]
    sig = row[4]
    for e in range(1,sEvent):
        lookup = "%s.%s.%s.%s" % (wfo, phenomena, sig, e)
        if lookup not in missing:
            add_missing(wfo, phenomena, sig, e)
            print "Warning Missing WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, 
                                                            phenomena, e)
      
    for eventid in range(sEvent, eEvent):
        sql = """SELECT gtype, count(*) as c from warnings_%s WHERE wfo = '%s' 
           and phenomena = '%s' and eventid = '%s' and significance = '%s' 
           GROUP by gtype""" % (YEAR, wfo, phenomena, eventid, sig)
        pcursor2.execute( sql )
        polyCount = 0
        cntyCount = 0
        for row2 in pcursor2:
            if (row2[0] == "P"): polyCount = int(row2[1])
            if (row2[0] == "C"): cntyCount = int(row2[1])

        if (cntyCount == 0 and polyCount == 0):
            lookup = "%s.%s.%s.%s" % (wfo, phenomena, sig, eventid)
        if lookup not in missing:
            add_missing(wfo, phenomena, sig, eventid)
            print "Warning Missing WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, 
                                                        phenomena, eventid)
        elif (polyCount == 0):
            print "SBW Missing     WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, 
                                                        phenomena, eventid)
        elif (cntyCount == 0):
            print "County Missing  WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, 
                                                        phenomena, eventid)
        elif (polyCount > 1):
            print "Duplicate SBW   WFO: %s PHENOMENA: %s EVENTID: %s" % (wfo, 
                                                        phenomena, eventid)
            sql = """DELETE from warnings_%s WHERE oid IN (
         SELECT max(oid) as m from warnings_%s WHERE wfo = '%s' 
         and phenomena = '%s' and eventid = '%s' and significance = '%s' 
         and gtype = 'P')""" % (mx.DateTime.now().year, YEAR,
          wfo, phenomena, eventid, sig)
            pcursor2.execute( sql )
            sql = """DELETE from warnings_%s WHERE oid IN (
              select m from (
select ugc,  max(oid) as m, count(oid) as c from warnings_%s WHERE wfo = '%s' 
and phenomena = '%s' and eventid = '%s' and significance = '%s' 
and gtype = 'C' GROUP by ugc) as foo WHERE c > 1)""" % (YEAR, YEAR,
          wfo, phenomena, eventid, sig)
            pcursor2.execute( sql )
      
pcursor2.close()
POSTGIS.commit()
POSTGIS.close()
