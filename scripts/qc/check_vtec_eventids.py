"""
My purpose in life is to daily check the VTEC database and see if there are
any IDs that are missing.  daryl then follows up with the weather bureau
reporting anything he finds after an investigation.
"""
import datetime
import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
pcursor = POSTGIS.cursor()
pcursor2 = POSTGIS.cursor()

YEAR = datetime.datetime.now().year - 1

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

# Gap analysis!
sql = """
with data as (
    select distinct wfo, phenomena, significance, eventid 
    from warnings_%s) 

 SELECT wfo, eventid, phenomena, significance, delta from
  (SELECT wfo, eventid, phenomena, significance, 
  eventid - lag(eventid) OVER (PARTITION by wfo, phenomena, significance 
                               ORDER by eventid ASC) as delta 
  from data) as foo 
 WHERE delta > 1 ORDER by wfo ASC
""" % (YEAR, )
pcursor.execute( sql )
for row in pcursor:
    phenomena = row[2]
    wfo = row[0]
    sig = row[3]
    gap = row[4]
    eventid = row[1]
    
    # Skip these
    if (wfo in ('NHC') or 
        phenomena in ('TR', 'HU') or
        (phenomena in ('TO', 'SV') and sig == 'A')):
        continue
    
    for e in range(eventid - gap, eventid):
        lookup = "%s.%s.%s.%s" % (wfo, phenomena, sig, e)
        if lookup in missing:
            continue
        add_missing(wfo, phenomena, sig, e)
        print "WWA missing WFO: %s phenomena: %s sig: %s eventid: %s" % (wfo, 
                                                            phenomena, sig, e)
      
#pcursor2.close()
#POSTGIS.commit()
#POSTGIS.close()
