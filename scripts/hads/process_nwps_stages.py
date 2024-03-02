"""Sync NWPS entries for flood stages!

Called from windrose/daily_drive_network.py
"""

import sys

import requests
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def process_site(mcursor, nwsli, meta):
    """Do our processing work"""

    url = f"https://preview-api.water.noaa.gov/nwps/v1/gauges/{nwsli}"

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
        UPDATE stations SET sigstage_low = %s,
        sigstage_action = %s,
        sigstage_bankfull = %s,
        sigstage_flood = %s,
        sigstage_moderate = %s,
        sigstage_major = %s,
        sigstage_record = %s
        WHERE iemid = %s
    """,
        (
            meta.get("sigstage_low"),
            meta.get("sigstage_action"),
            meta.get("sigstage_bankfull"),
            meta.get("sigstage_flood"),
            meta.get("sigstage_moderate"),
            meta.get("sigstage_major"),
            meta.get("sigstage_record"),
            meta["iemid"],
        ),
    )


def main(argv):
    """Go Main Go"""
    nt = NetworkTable(argv[1])
    with get_dbconn("mesosite") as dbconn:
        for sid, meta in nt.sts.items():
            mcursor = dbconn.cursor()
            process_site(mcursor, sid, meta)
            mcursor.close()
            dbconn.commit()


if __name__ == "__main__":
    main(sys.argv)
