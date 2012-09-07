"""
 Squawk to daryl about unknown HADS sites

Run from RUN_2AM.sh
"""
import iemdb
HADS = iemdb.connect('hads')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()

print 'Unknown NWSLIs from DCPish sites'
hcursor.execute("""
 select nwsli, count(*) as tot, max(product), 
 count(distinct substr(product,1,8)), 
 count(distinct product),
 sum(case when substr(nwsli,4,2) = 'I4' then 1 else 0 end) as priority 
 from unknown 
 where nwsli ~ '[A-Z]{4}[0-9]'
 GROUP by nwsli ORDER by priority DESC, tot DESC LIMIT 7
""")
for row in hcursor:
    print '%7s Tot:%4s Days:%2s Products: %s %s' % (row[0], row[1], row[3], 
      row[4], row[2])
    hcursor2.execute("""
    DELETE from unknown where nwsli = %s
    """, (row[0],))

print 'Unknown NWSLIs from COOPish sites'
hcursor.execute("""
 select nwsli, count(*) as tot, max(product), 
 count(distinct substr(product,1,8)), 
 count(distinct product),
 sum(case when substr(nwsli,4,2) = 'I4' then 1 else 0 end) as priority
 from unknown 
 WHERE network ~* 'COOP'
 and nwsli ~ '[A-Z]{4}[0-9]' GROUP by nwsli ORDER by priority DESC, tot DESC LIMIT 5
""")
for row in hcursor:
    print 'COOP %7s Tot:%4s Days:%2s Products: %s %s' % (row[0], row[1], 
     row[3], row[4], row[2])
    hcursor2.execute("""
    DELETE from unknown where nwsli = %s
    """, (row[0],))

   
HADS.commit()

ASOS = iemdb.connect('asos')
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

print 'Unknown IDs from ASOSish sites'
acursor.execute("""
 select id, count(*), max(valid) from unknown 
 GROUP by id ORDER by count DESC LIMIT 5
""")
for row in acursor:
    print 'ASOS %7s %5s %s' % (row[0], row[1], row[2])
    acursor2.execute("""
    DELETE from unknown where id = %s
    """, (row[0],))

ASOS.commit()

