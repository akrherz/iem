import psycopg2
import sys

PGCONN = psycopg2.connect(database='postgis', host='localhost', port=5555,
                          user='mesonet')
CURSOR = PGCONN.cursor()
CURSOR2 = PGCONN.cursor()

from pyiem.nws.products.vtec import parser as vtecparser

def supplement_ugcs():
    
    done = []
    for yr in range(2014,1986,-1):
        print "___________ Processing Year: %s ____________" % (yr,)
        CURSOR.execute("""SELECT geom, ugc, wfo from warnings_"""+str(yr)+"""
        WHERE gid is null and not ST_IsEmpty(geom) and length(ugc) = 6
        """)
        for row in CURSOR:
            ugc = row[1]
            if ugc in done:
                continue
            done.append(ugc)
            CURSOR2.execute("""SELECT ugc from ugcs where ugc = %s""", (ugc,))
            if CURSOR2.rowcount != 0:
                continue
            print 'INSERT %s' % (ugc,)
            CURSOR2.execute("""INSERT into ugcs(ugc, name, state, wfo,
            begin_ts, geom) VALUES (%s, %s, %s, %s, '1980-01-01', 
            (SELECT geom from warnings_"""+str(yr)+""" WHERE
            gid is null and not ST_IsEmpty(geom) and ugc = %s LIMIT 1))
            """, (ugc, 'Unknown %s' % (ugc,), ugc[:2], row[2], ugc))
            CURSOR2.execute("""UPDATE ugcs SET
            simple_geom = ST_Simplify(geom, 0.01),
             centroid = ST_Centroid(geom) WHERE ugc = %s""", (ugc,))
        

def fix_non6_ugcs():
    
    for yr in range(2008, 2012):
        print "___________ Processing Year: %s ____________" % (yr,)
        CURSOR.execute("""SELECT wfo, eventid, phenomena, significance, report,
        ST_astext(geom), ugc, oid
        from warnings_"""+str(yr)+""" WHERE gid is null and
        not ST_IsEmpty(geom) and length(ugc) = 6""")
        for row in CURSOR:
            # Okay, we have some work to do here...
            print "NULL GID! %s.%s.%s.%s.%s %s" % (yr, row[0], row[1], row[2],
                                               row[3], row[6])
            try:
                prod = vtecparser(row[4])
            except Exception as exp:
                print "FAILURE!", exp
                continue

            ugc = row[6]
            CURSOR2.execute("""SELECT get_gid(%s,%s)""", (ugc, prod.valid))
            row2 = CURSOR2.fetchone()
            if row2[0] is None:
                print 'Can not find UGC: %s Valid: %s' % (ugc, prod.valid)
                CURSOR2.execute("""SELECT gid from ugcs where ugc = %s""",
                                (ugc,))
                if CURSOR2.rowcount == 1:
                    gid = CURSOR2.fetchone()[0]
                    print '  Forcing to gid: %s ...' % (gid,)
                    CURSOR2.execute("""UPDATE warnings_"""+str(yr)+""" 
                    SET gid = %s WHERE oid = %s
                    """, (gid, row[7]))

fix_non6_ugcs()
#supplement_ugcs()
CURSOR2.close()
CURSOR.close()
PGCONN.commit()
PGCONN.close()