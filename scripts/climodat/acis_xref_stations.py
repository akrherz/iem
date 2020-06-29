"""Mine the ACIS station cross-reference."""
import sys

import requests
from pyiem.util import get_dbconn, logger
from pyiem.network import Table as NetworkTable
from pyiem.reference import ncei_state_codes

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnMeta"
MYATTR = "TRACKS_STATION"


def main(argv):
    """Do the query and work."""
    state = argv[1]
    network = "%sCLIMATE" % (state,)
    nt = {
        network: NetworkTable(network),
        "%s_COOP" % (state,): NetworkTable("%s_COOP" % (state,)),
        "%s_ASOS" % (state,): NetworkTable("%s_ASOS" % (state,)),
    }
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    for sid in nt[network].sts:
        if sid[2:] == "0000" or sid[2] == "C":
            continue
        current = nt[network].sts[sid]["attributes"].get(MYATTR)
        if current is not None:
            continue
        acis_station = "%s%s" % (ncei_state_codes[state], sid[2:])
        payload = {"sids": acis_station}
        req = requests.post(SERVICE, json=payload)
        j = req.json()
        meta = j["meta"]
        if not meta:
            LOG.info("ACIS lookup of %s failed, sid: %s", acis_station, sid)
            continue
        meta = meta[0]
        LOG.info("%s %s", sid, meta["sids"])
        for entry in meta["sids"]:
            tokens = entry.split()
            if tokens[1] in ["3", "7"]:
                to_track = tokens[0]
                to_network = "%s_%s" % (
                    state,
                    "COOP" if tokens[1] == "7" else "ASOS",
                )
                LOG.info("    %s -> %s %s", sid, to_track, to_network)
                if to_track not in nt[to_network].sts:
                    LOG.info("    ERROR %s is unknown!", to_track)
                    continue
                value = "%s|%s" % (to_track, to_network)
                if tokens[1] == "3":
                    cursor.execute(
                        """
                        UPDATE stations SET temp24_hour = 0, precip24_hour = 0
                        WHERE iemid = %s
                    """,
                        (nt[network].sts[sid]["iemid"],),
                    )
                cursor.execute(
                    """
                    INSERT into station_attributes(iemid, attr, value)
                    VALUES (%s, %s, %s)
                """,
                    (nt[network].sts[sid]["iemid"], MYATTR, value),
                )
                break
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
