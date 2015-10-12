"""
 Squawk to daryl about unknown HADS sites

Run from RUN_2AM.sh
"""
import psycopg2
HADS = psycopg2.connect(database='hads', host='iemdb')
ACCESS = psycopg2.connect(database='iem', host='iemdb')
hcursor = HADS.cursor()
hcursor2 = HADS.cursor()
acursor = ACCESS.cursor()

print('----- Unknown NWSLIs from DCPish sites -----')
for priority in ['priority DESC', 'maxp ASC']:
    hcursor.execute("""
     select nwsli, count(*) as tot, max(product) as maxp,
     count(distinct substr(product,1,8)),
     count(distinct product),
     sum(case when substr(nwsli,4,2) = 'I4' then 1 else 0 end) as priority
     from unknown
     where nwsli ~ '^[A-Z]{4}[0-9]$'
     GROUP by nwsli ORDER by """ + priority + """, tot DESC LIMIT 7
    """)
    for row in hcursor:
        print '%7s Tot:%4s Days:%2s Products: %s %s' % (row[0], row[1], row[3],
                                                        row[4], row[2])
        # Get vars reported for this site
        acursor.execute("""
            SELECT valid, physical_code || duration || source ||
            extremum || probability as p, value from current_shef
            WHERE station = %s ORDER by p ASC""", (row[0],))
        for row2 in acursor:
            print '    %s %s %s' % (row2[0], row2[1], row2[2])

print '----- Unknown NWSLIs from COOPish sites -----'
hcursor.execute("""
 select nwsli, count(*) as tot, max(product),
 count(distinct substr(product,1,8)),
 count(distinct product),
 sum(case when substr(nwsli,4,2) = 'I4' then 1 else 0 end) as priority
 from unknown
 WHERE network ~* 'COOP'
 and nwsli ~ '^[A-Z]{4}[0-9]$' GROUP by nwsli
 ORDER by priority DESC, tot DESC LIMIT 5
""")
for row in hcursor:
    print 'COOP %7s Tot:%4s Days:%2s Products: %s %s' % (row[0], row[1],
                                                         row[3], row[4],
                                                         row[2])
    # Get vars reported for this site
    acursor.execute("""SELECT valid, physical_code || duration || source ||
    extremum || probability as p, value from current_shef WHERE station = %s
    ORDER by p ASC""", (row[0],))
    for row2 in acursor:
        print '    %s %s %s' % (row2[0], row2[1], row2[2])


HADS.commit()

ASOS = psycopg2.connect(database='asos', host='iemdb')
acursor = ASOS.cursor()
acursor2 = ASOS.cursor()

print '----- Unknown IDs from METAR sites -----'
acursor.execute("""
 select id, count(*), max(valid) from unknown
 GROUP by id ORDER by count DESC
""")
for row in acursor:
    print 'ASOS %7s %5s %s' % (row[0], row[1], row[2])
    acursor2.execute("""
    DELETE from unknown where id = %s
    """, (row[0],))

ASOS.commit()


def print_blank_sname():
    pgconn = psycopg2.connect(database='mesosite', host='iemdb')
    cursor = pgconn.cursor()
    cursor.execute("""SELECT id, network from stations
    WHERE name is null or name = '' ORDER by iemid ASC LIMIT 5""")

    print '------ Sites with empty station names ------'
    for row in cursor:
        print "%10s %s" % (row[0], row[1])

print_blank_sname()
