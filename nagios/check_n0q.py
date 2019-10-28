"""
Check the production of N0Q data!
"""
from __future__ import print_function
import json
import datetime
import sys


def main(argv):
    """Do Great Things"""
    prod = argv[1]

    j = json.load(
        open("/home/ldm/data/gis/images/4326/USCOMP/%s_0.json" % (prod,))
    )
    prodtime = datetime.datetime.strptime(
        j["meta"]["valid"], "%Y-%m-%dT%H:%M:%SZ"
    )
    radarson = int(j["meta"]["radar_quorum"].split("/")[0])
    gentime = j["meta"]["processing_time_secs"]

    utcnow = datetime.datetime.utcnow()
    latency = (utcnow - prodtime).total_seconds()

    stats = "gentime=%s;180;240;300 radarson=%s;100;75;50" % (
        gentime,
        radarson,
    )

    if gentime < 300 and radarson > 50 and latency < 60 * 10:
        print("OK |%s" % (stats))
        return 0
    if gentime > 300:
        print("CRITICAL - gentime %s|%s" % (gentime, stats))
        return 2
    if latency > 600:
        print(
            "CRITICAL - radtime:%s latency:%ss|%s" % (prodtime, latency, stats)
        )
        return 2
    if radarson < 50:
        print("CRITICAL - radarson %s|%s" % (radarson, stats))
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
