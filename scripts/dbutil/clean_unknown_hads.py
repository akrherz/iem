"""
I look at the unknown HADS table and see if any of these stations exist
in the mesosite database, if so, then I set online to true!

Run from RUN_2AM.sh
"""

from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go"""
    hads = get_dbconn("hads")
    mesosite = get_dbconn("mesosite")
    hcursor = hads.cursor()
    hcursor2 = hads.cursor()
    mcursor = mesosite.cursor()

    # look for unknown
    hcursor.execute(
        "SELECT nwsli, network, max(product) from unknown "
        "WHERE length(nwsli) = 5 GROUP by nwsli, network ORDER by nwsli ASC"
    )
    for row in hcursor:
        nwsli = row[0]
        network = row[1]
        mcursor.execute("SELECT online from stations where id = %s", (nwsli,))
        row2 = mcursor.fetchone()
        if row2 is None:
            continue
        if not row2[0]:
            print(
                f"Site {nwsli} [{network}] {row[2]} was unknown, "
                "but is in mesosite"
            )
            mcursor.execute(
                "update stations SET online = 't' where id = %s "
                "and online = 'f'",
                (nwsli,),
            )
        else:
            print(
                f"Site {nwsli} [{network}] {row[2]} was unknown, "
                "but online in DB?"
            )
        hcursor2.execute("DELETE from unknown where nwsli = %s", (nwsli,))

    hcursor2.close()
    hads.commit()
    mcursor.close()
    mesosite.commit()


if __name__ == "__main__":
    main()
