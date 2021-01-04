"""Mine ACIS for threaded stations."""

import requests
from pyiem.util import get_dbconn, logger
from pyiem.network import Table as NetworkTable
from pyiem.reference import ncei_state_codes

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnMeta"
MYATTR = "TRACKS_STATION"
# One offs needing manual effort
UNKNOWNS = ["LOXthr", "LHUthr", "CVGthr", "MQTthr", "FCAthr"]


def workflow(state):
    """Do the query and work."""
    network = "%sCLIMATE" % (state,)
    nt = {
        network: NetworkTable(network),
        "%s_COOP" % (state,): NetworkTable("%s_COOP" % (state,)),
        "%s_ASOS" % (state,): NetworkTable("%s_ASOS" % (state,)),
    }
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    payload = {"state": state.lower()}
    req = requests.post(SERVICE, json=payload)
    j = req.json()
    meta = j["meta"]
    for entry in meta:
        threadid = None
        for sid in entry["sids"]:
            if sid.find("thr 9") > 0:
                threadid = sid.split()[0]
        if threadid is None:
            continue
        if threadid in UNKNOWNS:
            LOG.info("skipping %s", threadid)
            continue
        iemid = "%sT%s" % (state, threadid[:3])
        if iemid in nt["%sCLIMATE" % (state,)].sts:
            LOG.info("%s is already known!", iemid)
            continue
        to_track = threadid[:-3]
        if state in ["AK", "HI"]:
            to_track = "P" + to_track
        if state == "PR":
            to_track = "T" + to_track
        to_network = "%s_%s" % (
            state,
            "COOP" if len(to_track) == 5 else "ASOS",
        )
        LOG.info("%s will be %s and tracking %s", threadid, iemid, to_track)
        if to_track not in nt[to_network].sts:
            LOG.info("Skipping, as %s not in %s", to_track, to_network)
            continue
        # Create station entry, we use the tracking station location for now
        geom = "SRID=4326;POINT(%s %s)" % (
            nt[to_network].sts[to_track]["lon"],
            nt[to_network].sts[to_track]["lat"],
        )
        cursor.execute(
            """
        INSERT into stations(id, name, state, country, elevation, network,
        online, plot_name, climate_site, metasite, geom, temp24_hour,
        precip24_hour) values (%s, %s, %s, %s, %s, %s, 't', %s, %s, 't',
        %s, 0, 0)
        returning iemid
        """,
            (
                iemid,
                entry["name"],
                state,
                "US",
                -999,
                "%sCLIMATE" % (state,),
                entry["name"],
                iemid,
                geom,
            ),
        )
        idnum = cursor.fetchone()[0]

        value = "%s|%s" % (to_track, to_network)
        cursor.execute(
            "INSERT into station_attributes(iemid, attr, value) "
            "VALUES (%s, %s, %s)",
            (idnum, MYATTR, value),
        )
    cursor.close()
    pgconn.commit()


def main():
    """Go Main Go."""
    states = list(ncei_state_codes.keys())
    states.sort()
    for statecode in states:
        workflow(statecode)


if __name__ == "__main__":
    main()
