# Squawk to daryl about unknown HADS sites
import iemdb
HADS = iemdb.connect('hads')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()

hcursor.execute("""
select nwsli, count(*), max(product) from unknown GROUP by nwsli ORDER by count DESC LIMIT 5
""")
for row in hcursor:
    print '%7s %5s %s' % (row[0], row[1], row[2])
    hcursor2.execute("""
    DELETE from unknown where nwsli = %s
    """, (row[0],))
    
HADS.commit()