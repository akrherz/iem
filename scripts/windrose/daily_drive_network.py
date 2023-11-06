"""Pick two networks to drive windroses for.

Called from RUN_2AM.sh script
"""
import subprocess

from pyiem.util import get_dbconn, logger

LOG = logger()
CACHEDIR = "/mesonet/share/windrose/"


def do_network(network):
    """Process a network"""
    # Update the STS while we are at it, this will help the database get
    # stuff cached too
    if network.find("_ASOS") > 0:
        subprocess.call(
            ["python", "../dbutil/compute_alldata_sts.py", "asos", network]
        )
    elif network.find("_DCP") > 0:
        # Special Logic to compute archive period.
        subprocess.call(["python", "../dbutil/compute_hads_sts.py", network])
        # Update stage details.
        subprocess.call(["python", "../hads/process_ahps_xml.py", network])
    elif network.find("_RWIS") > 0:
        subprocess.call(
            ["python", "../dbutil/compute_alldata_sts.py", "rwis", network],
        )
    subprocess.call(["python", "drive_network_windrose.py", network])


def main():
    """Main"""
    with get_dbconn("mesosite") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "with data as (SELECT id from networks where "
            "(id ~* '_ASOS' or id ~* '_DCP' or id ~* 'RWIS') "
            "ORDER by windrose_update ASC NULLS FIRST LIMIT 2) "
            "UPDATE networks n SET windrose_update = now() FROM data d "
            "WHERE d.id = n.id RETURNING n.id"
        )
        rows = cursor.fetchall()

    for row in rows:
        network = row[0]
        LOG.warning("Driving network %s", network)
        do_network(network)


if __name__ == "__main__":
    main()
