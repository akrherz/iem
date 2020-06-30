"""Ingest the rich metadata found within the AHPS2 website!
"""
import sys

import requests
from twisted.words.xish import xpath, domish
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def process_site(mcursor, nwsli, network):
    """Do our processing work"""

    url = (
        "http://water.weather.gov/ahps2/hydrograph_to_xml.php?"
        "gage=%s&output=xml"
    ) % (nwsli,)

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
            print("No results for %s" % (nwsli,))
            return
    except Exception as exp:
        print("DOWNLOAD ERROR")
        print(url)
        print(exp)
        return
    try:
        elementStream.parse(xml)
    except Exception as exp:
        print("XML ERROR")
        print(url)
        print(exp)
        return

    elem = results[0]

    nodes = xpath.queryForNodes("/site/sigstages", elem)
    if nodes is None:
        print("No data found for %s" % (nwsli,))
        return

    sigstages = nodes[0]
    data = {
        "id": nwsli,
        "network": network,
        "sigstage_low": None,
        "sigstage_action": None,
        "sigstage_bankfull": None,
        "sigstage_flood": None,
        "sigstage_moderate": None,
        "sigstage_major": None,
        "sigstage_record": None,
    }
    for s in sigstages.children:
        val = str(s)
        if val == "":
            continue
        data["sigstage_%s" % (s.name,)] = float(val)

    if "sigstage_low" not in data:
        print("No Data %s %s" % (nwsli, network))
        return

    print(
        ("%s %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f %5.1f")
        % (
            data["id"],
            data["sigstage_low"] or -99,
            data["sigstage_action"] or -99,
            data["sigstage_bankfull"] or -99,
            data["sigstage_flood"] or -99,
            data["sigstage_moderate"] or -99,
            data["sigstage_major"] or -99,
            data["sigstage_record"] or -99,
        )
    )
    mcursor.execute(
        """
        UPDATE stations SET sigstage_low = %(sigstage_low)s,
        sigstage_action = %(sigstage_action)s,
        sigstage_bankfull = %(sigstage_bankfull)s,
        sigstage_flood = %(sigstage_flood)s,
        sigstage_moderate = %(sigstage_moderate)s,
        sigstage_major = %(sigstage_major)s,
        sigstage_record = %(sigstage_record)s
        WHERE id = %(id)s and network = %(network)s
    """,
        data,
    )


def main():
    """Go Main Go"""
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    print(
        ("%5s %5s %5s %5s %5s %5s %5s %5s")
        % ("NWSLI", "LOW", "ACTN", "BANK", "FLOOD", "MOD", "MAJOR", "REC")
    )
    net = sys.argv[1]
    nt = NetworkTable(net)
    for sid in nt.sts:
        process_site(mcursor, sid, net)
    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
