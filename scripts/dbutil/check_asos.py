"""Check that ASOS sites are actually online

Looks at our archive for ASOS sites which we think are online, but have
never reported data.  If so, set them offline!
"""
from __future__ import print_function

from pyiem.util import get_dbconn


def main():
    """Go"""
    pgconn_asos = get_dbconn("asos")
    acursor = pgconn_asos.cursor()
    pgconn_mesosite = get_dbconn("mesosite")
    mcursor = pgconn_mesosite.cursor()
    mcursor2 = pgconn_mesosite.cursor()
    pgconn_iem = get_dbconn("iem")
    icursor = pgconn_iem.cursor()

    # Find blank start stations!
    mcursor.execute(
        """
        select id, network from stations where archive_begin is null
        and network ~* 'ASOS' and online ORDER by network
    """
    )
    for row in mcursor:
        sid = row[0]
        network = row[1]
        # Look in current for valid
        icursor.execute(
            """
          SELECT valid from current c JOIN stations t on (t.iemid = c.iemid)
          where t.id = %s and t.network = %s
          """,
            (sid, network),
        )
        row = icursor.fetchone()
        if row:
            valid = row[0]
            if valid.year == 1980:
                print("No current data for %s %s" % (sid, network))
        else:
            mcursor2.execute(
                """ UPDATE stations SET online = 'f' where
                id = %s and network = %s """,
                (sid, network),
            )
            print("Setting %s %s to offline" % (sid, network))
            continue
        acursor.execute(
            """
           SELECT min(valid) from alldata where station = %s
          """,
            (sid,),
        )
        row = acursor.fetchone()
        print("%s %s IEMDB: %s ASOSDB: %s" % (sid, network, valid, row[0]))

    pgconn_mesosite.close()


if __name__ == "__main__":
    main()
