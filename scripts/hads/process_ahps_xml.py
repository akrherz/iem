"""Ingest the rich metadata found within the AHPS2 website!"""
import sys

import requests
from twisted.words.xish import xpath, domish
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def process_site(mcursor, nwsli, meta):
    """Do our processing work"""

    url = (
        "http://water.weather.gov/ahps2/hydrograph_to_xml.php?"
        f"gage={nwsli}&output=xml"
    )

    elementStream = domish.elementStream()
    roots = []
    results = []
    elementStream.DocumentStartEvent = roots.append
    elementStream.ElementEvent = lambda elem: roots[0].addChild(elem)
    elementStream.DocumentEndEvent = lambda: results.append(roots[0])
    try:
        req = requests.get(url, timeout=30)
        xml = req.content
        if xml.strip() == "No results found for this gage.":
            LOG.info("No results for %s", nwsli)
            return
    except Exception as exp:
        LOG.exception(exp)
        return
    try:
        elementStream.parse(xml)
    except Exception as exp:
        LOG.exception(exp)
        return

    elem = results[0]

    nodes = xpath.queryForNodes("/site/sigstages", elem)
    if nodes is None:
        LOG.info("No sigstages data found for %s", nwsli)
        return

    sigstages = nodes[0]
    diction = "low action bankfull flood moderate major record".split()
    is_new = False
    msg = ""
    for s in sigstages.children:
        if s.name not in diction:
            continue
        val = str(s)
        if val == "":
            continue
        key = f"sigstage_{s.name}"
        val = float(val)
        if val < 0:
            continue
        # is this updated info?
        current = meta.get(key)
        if current is None or abs(current - val) > 0.01:
            is_new = True
            msg += f"{s.name}: {current}->{val} "
        meta[key] = val
    if not is_new:
        return

    LOG.debug("updating %s with %s", nwsli, msg)
    mcursor.execute(
        """
        UPDATE stations SET sigstage_low = %(sigstage_low)s,
        sigstage_action = %(sigstage_action)s,
        sigstage_bankfull = %(sigstage_bankfull)s,
        sigstage_flood = %(sigstage_flood)s,
        sigstage_moderate = %(sigstage_moderate)s,
        sigstage_major = %(sigstage_major)s,
        sigstage_record = %(sigstage_record)s
        WHERE iemid = %(iemid)s
    """,
        meta,
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
