# Squawk to daryl about unknown HADS sites
import iemdb
HADS = iemdb.connect('hads')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()

print 'Unknown NWSLIs from DCPish sites'
hcursor.execute("""
 select nwsli, count(*), max(product) from unknown 
 where product !~* 'KTIR'
 GROUP by nwsli ORDER by count DESC LIMIT 5
""")
for row in hcursor:
    print '%7s %5s %s' % (row[0], row[1], row[2])
    hcursor2.execute("""
    DELETE from unknown where nwsli = %s
    """, (row[0],))

print 'Unknown NWSLIs from COOPish sites'
hcursor.execute("""
 select nwsli, count(*), max(product) from unknown 
 WHERE network ~* 'COOP' GROUP by nwsli ORDER by count DESC LIMIT 5
""")
for row in hcursor:
    print 'COOP %7s %5s %s' % (row[0], row[1], row[2])
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

