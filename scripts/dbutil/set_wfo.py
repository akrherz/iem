"""Assign a WFO to sites in the metadata tables that have no WFO set
"""

import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

# Find sites we need to check on
mcursor.execute("""
    select s.id, s.iemid, s.network
    from stations s WHERE
    (s.wfo IS NULL or s.wfo = '') and s.country = 'US'
""")

for row in mcursor:
    sid = row[0]
    iemid = row[1]
    network = row[2]
    # Look for matching WFO
    mcursor2.execute("""
    select c.wfo
    from stations s, cwa c WHERE
    s.geom && c.the_geom and ST_contains(c.the_geom, s.geom)
    and iemid = %s
    """, (iemid, ))
    if mcursor2.rowcount > 0:
        row2 = mcursor2.fetchone()
        wfo = row2[0]
        print(('Assinging WFO: %s to IEMID: %s ID: %s NETWORK: %s'
               ) % (wfo, iemid, sid, network))
        mcursor2.execute("""
            UPDATE stations SET wfo = '%s' WHERE iemid = %s
        """ % (wfo, iemid))
    else:
        print(('ERROR assigning WFO to IEMID: %s ID: %s NETWORK: %s'
               ) % (iemid, sid, network))


mcursor.close()
mcursor2.close()
MESOSITE.commit()
MESOSITE.close()
