'''
 Looks at our archive for ASOS sites which we think are online, but have
 never reported data.  If so, set them offline!
'''
import psycopg2
ASOS = psycopg2.connect(database='asos', host='iemdb')
acursor = ASOS.cursor()
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()

# Find blank start stations!
mcursor.execute("""
    select id, network from stations where archive_begin is null
    and network ~* 'ASOS' and online ORDER by network
""")
for row in mcursor:
    sid = row[0]
    network = row[1]
    # Look in current for valid
    icursor.execute("""
      SELECT valid from current c JOIN stations t on (t.iemid = c.iemid)
      where t.id = %s and t.network = %s
      """, (sid, network))
    row = icursor.fetchone()
    if row:
        valid = row[0]
        if valid.year == 1980:
            print 'No current data for %s %s' % (sid, network)
    else:
        mcursor2.execute(""" UPDATE stations SET online = 'f' where
            id = %s and network = %s """, (sid, network))
        print 'Setting %s %s to offline' % (sid, network)
        continue
    acursor.execute("""
       SELECT min(valid) from alldata where station = %s
      """, (sid,))
    row = acursor.fetchone()
    print '%s %s IEMDB: %s ASOSDB: %s' % (sid, network, valid, row[0])

MESOSITE.close()
