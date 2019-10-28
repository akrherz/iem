"""
Need something to set the time zone of networks
"""
from __future__ import print_function
from pyiem.util import get_dbconn


def main():
    """Go!"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor2 = pgconn.cursor()

    mcursor.execute(
        """
     SELECT id, name from networks where tzname is null
    """
    )

    for row in mcursor:
        netid = row[0]

        mcursor2.execute(
            """SELECT tzname, count(*) from stations
        where network = '%s' and tzname is not null
        GROUP by tzname ORDER by count DESC"""
            % (netid,)
        )
        row2 = mcursor2.fetchone()
        if row2 is None or row2[0] == "uninhabited":
            print("--> MISSING ID: %s" % (netid,))
        else:
            print("ID: %s TIMEZONE: %s" % (netid, row2[0]))
            mcursor2.execute(
                """UPDATE networks SET tzname = '%s'
            WHERE id = '%s' """
                % (row2[0], netid)
            )

    mcursor2.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
