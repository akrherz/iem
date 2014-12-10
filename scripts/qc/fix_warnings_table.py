import psycopg2
import sys

PGCONN = psycopg2.connect(database='postgis', host='localhost', port=5555,
                          user='mesonet')
CURSOR = PGCONN.cursor()
CURSOR2 = PGCONN.cursor()

from pyiem.nws.products.vtec import parser as vtecparser

def fix_non6_ugcs():
    
    for yr in range(2002, 2007):
        print "___________ Processing Year: %s ____________" % (yr,)
        CURSOR.execute("""SELECT wfo, eventid, phenomena, significance, report,
        ST_astext(geom) 
        from warnings_"""+str(yr)+""" WHERE gtype = 'P' """)
        for row in CURSOR:
            CURSOR2.execute("""SELECT * from sbw_"""+str(yr)+""" WHERE 
            wfo = %s and eventid = %s and phenomena = %s and significance = %s
            """, (row[0], row[1], row[2], row[3]))
            if CURSOR2.rowcount > 0:
                continue
            # Okay, we have some work to do here...
            print "MISSING! %s.%s.%s.%s.%s %s" % (yr, row[0], row[1], row[2],
                                               row[3], row[5])
            try:
                prod = vtecparser(row[4])
            except:
                print "FAILURE!"
                continue
            
            for segment in prod.segments:
                for vtec in segment.vtec:
                    if vtec.action != 'NEW':
                        print("  --> SKIP due to none NEW action: %s" % (
                                                            vtec.action))
                        continue
                    if vtec.status != 'O':
                        print("  --> SKIP due to none O status: %s" % (
                                                            vtec.status))
                        continue
                    print("  --> Insert %s %s" % (prod.valid.year, vtec))
                    try:
                        prod.do_sbw_geometry(CURSOR2, segment, vtec)
                    except Exception as exp:
                        print exp
                        print row[4]
                        sys.exit()

fix_non6_ugcs()
CURSOR2.close()
CURSOR.close()
PGCONN.commit()
PGCONN.close()