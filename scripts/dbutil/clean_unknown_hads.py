"""
 I look at the unknown HADS table and see if any of these stations exist
 in the mesosite database, if so, then I set online to true!

 Run from RUN_2AM.sh
"""

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    hads = get_dbconn("hads")
    mesosite = get_dbconn("mesosite")
    hcursor = hads.cursor()
    hcursor2 = hads.cursor()
    mcursor = mesosite.cursor()

    # look for unknown
    hcursor.execute(
        "SELECT distinct nwsli, network from unknown WHERE length(nwsli) = 5"
    )
    for row in hcursor:
        nwsli = row[0]
        network = row[1]
        mcursor.execute("SELECT online from stations where id = %s", (nwsli,))
        row = mcursor.fetchone()
        if row is None:
            continue
        elif not row[0]:
            print(
                ("Site %s [%s] was unknown, but is in mesosite")
                % (nwsli, network)
            )
            mcursor.execute(
                "update stations SET online = 't' where id = %s "
                "and online = 'f'",
                (nwsli,),
            )
            hcursor2.execute("DELETE from unknown where nwsli = %s", (nwsli,))
        else:
            print(
                ("Site %s [%s] was unknown, but online in DB?")
                % (nwsli, network)
            )
            hcursor2.execute("DELETE from unknown where nwsli = %s", (nwsli,))

    hcursor2.close()
    hads.commit()
    mcursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
