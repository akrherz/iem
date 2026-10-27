"""Sync NWPS entries for flood stages!

Called from windrose/daily_drive_network.py
"""

import click
import requests
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()
DICTION = ("action", "minor", "moderate", "major")


def process_site(mcursor, nwsli: str, meta: dict):
    """Do our processing work"""

    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{nwsli}"

    try:
        res = requests.get(url, timeout=30)
        if res.status_code != 200:
            LOG.info("Failed to fetch %s, got %s", url, res.status_code)
            return
        res = res.json()
        if res.get("code") == 5:
            LOG.info("No data found for %s", nwsli)
            return
    except Exception as exp:
        LOG.exception(exp)
        return

    msg = ""
    for name, entry in res.get("flood", {}).get("categories", {}).items():
        if name not in DICTION:
            LOG.info("Ignoring unknown label %s for %s", name, nwsli)
            continue
        key = f"sigstage_{name}"
        val = entry["stage"]
        if val < 0:
            continue
        # is this updated info?
        current = meta.get(key)
        if current is None or abs(current - val) > 0.01:
            msg += f"{name}: {current}->{val} "
        meta[key] = val
    if msg == "":
        return

    LOG.info("updating %s with %s", nwsli, msg)
    mcursor.execute(
        """
        UPDATE stations SET
        sigstage_action = %s,
        sigstage_minor = %s,
        sigstage_moderate = %s,
        sigstage_major = %s
        WHERE iemid = %s
    """,
        (
            meta.get("sigstage_action"),
            meta.get("sigstage_minor"),
            meta.get("sigstage_moderate"),
            meta.get("sigstage_major"),
            meta["iemid"],
        ),
    )


@click.command()
@click.option("--network", required=True, help="IEM Network Identifier")
def main(network):
    """Go Main Go"""
    nt = NetworkTable(network)
    with get_dbconn("mesosite", rw=True) as dbconn:
        for sid, meta in nt.sts.items():
            mcursor = dbconn.cursor()
            process_site(mcursor, sid, meta)
            mcursor.close()
            dbconn.commit()


if __name__ == "__main__":
    main()
