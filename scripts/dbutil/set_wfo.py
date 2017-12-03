"""Assign a WFO to sites in the metadata tables that have no WFO set
"""
from __future__ import print_function

from pyiem.util import get_dbconn


def main():
    """Go Main"""
    mesosite = get_dbconn('mesosite')
    mcursor = mesosite.cursor()
    mcursor2 = mesosite.cursor()

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
        select c.wfo, ST_Distance(c.the_geom, s.geom) as dist
        from stations s, cwa c WHERE
        iemid = %s ORDER by dist ASC LIMIT 1
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
    mesosite.commit()
    mesosite.close()


if __name__ == '__main__':
    main()
