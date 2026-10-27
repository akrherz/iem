"""Pick two networks to drive windroses for.

Called from RUN_2AM.sh script
"""

import subprocess

from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()
CACHEDIR = "/mesonet/share/windrose/"


def do_network(network: str):
    """Process a network"""
    # Update the STS while we are at it, this will help the database get
    # stuff cached too
    if "_ASOS" in network:
        subprocess.run(
            [
                "python",
                "../dbutil/compute_alldata_sts.py",
                "--dbname=asos",
                f"--network={network}",
            ],
            check=True,
        )
    elif "_DCP" in network:
        # Special Logic to compute archive period.
        subprocess.run(
            [
                "python",
                "../dbutil/compute_hads_sts.py",
                f"--network={network}",
            ],
            check=True,
        )
        # Update stage details.
        subprocess.run(
            [
                "python",
                "../hads/process_nwps_stages.py",
                f"--network={network}",
            ],
            check=True,
        )
    elif "_RWIS" in network:
        subprocess.run(
            [
                "python",
                "../dbutil/compute_rwis_sts.py",
                f"--network={network}",
            ],
            check=True,
        )
    subprocess.run(
        ["python", "drive_network_windrose.py", "--network", network],
        check=True,
    )


def main():
    """Main"""
    with get_dbconn("mesosite", rw=True) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        with data as (SELECT id from networks where
            (id ~* '_ASOS' or id ~* '_DCP' or id ~* 'RWIS')
            ORDER by windrose_update ASC NULLS FIRST LIMIT 2)
        UPDATE networks n SET windrose_update = now() FROM data d
        WHERE d.id = n.id RETURNING n.id
            """
        )
        rows = cursor.fetchall()

    for row in rows:
        network = row[0]
        LOG.warning("Driving network %s", network)
        do_network(network)


if __name__ == "__main__":
    main()
