"""
 Loop over sites that we think are solely COOP, but report many times per day
 and so are likely DCP
"""
from __future__ import print_function
import subprocess

from pyiem.util import get_dbconn


def main():
    """GO!"""
    ipgconn = get_dbconn("iem")
    icursor = ipgconn.cursor()
    icursor2 = ipgconn.cursor()
    mpgconn = get_dbconn("mesosite")
    mcursor = mpgconn.cursor()
    mcursor2 = mpgconn.cursor()

    # Look for over-reporting COOPs
    icursor.execute(
        """
     select id, network, count(*), max(raw) from current_log c JOIN stations s
     ON (s.iemid = c.iemid)
     where network ~* 'COOP' and valid > 'TODAY'::date
     GROUP by id, network ORDER by count DESC
    """
    )
    for row in icursor:
        sid = row[0]
        network = row[1]
        if row[2] < 5:
            continue
        # Look for how many entries are in mesosite
        mcursor.execute(
            """SELECT network from stations where id = %s
          """,
            (sid,),
        )
        if mcursor.rowcount == 1:
            newnetwork = network.replace("_COOP", "_DCP")
            print(
                "We shall switch %s from %s to %s" % (sid, network, newnetwork)
            )
            mcursor2.execute(
                """
                UPDATE stations SET network = '%s' WHERE id = '%s'
            """
                % (newnetwork, sid)
            )
        if mcursor.rowcount == 2:
            networks = []
            for row2 in mcursor:
                networks.append(row2[0])
            if network.replace("_COOP", "_DCP") in networks:
                print("Deleting COOP variant for sid: %s" % (sid,))
                cmd = ("python delete_station.py %s %s") % (network, sid)
                subprocess.call(cmd, shell=True)

    ipgconn.commit()
    icursor2.close()
    mpgconn.commit()
    mcursor.close()


if __name__ == "__main__":
    main()
