"""Setup some baseline archive folders / files to prevent 404s

 - RIDGE folders
 - NOAAport archive files

Since we have web scrapers, we need to have empty folders to keep the Server
from having lots of 404s

called from RUN_0Z.sh
"""
import os
import subprocess
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import utc

PRODS = {
    "NEXRAD": ["N0B", "N0S"],
    "TWDR": ["TZL", "TV0"],
}
PILS = (
    "LSR|FWW|CFW|TCV|RFW|FFA|SVR|TOR|SVS|SMW|MWS|NPW|WCN|WSW|EWW|FLS"
    "|FLW|SPS|SEL|SWO|FFW|DSW|SQW"
).split("|")


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        ts = utc()
    else:
        ts = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    nt = NetworkTable(["NEXRAD", "TWDR"])
    for sid in nt.sts:
        for prod in PRODS[nt.sts[sid]["network"]]:
            pqstr = (
                f"data d {ts:%Y%m%d%H%M} GIS/ridge/{sid}/{prod} "
                f"GIS/ridge/{sid}/{prod} bogus"
            )
            subprocess.call(["pqinsert", "-i", "-p", pqstr, "/etc/fstab"])

    # Do noaaport text
    basedir = ts.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/noaaport")
    if os.path.isdir(basedir):
        os.chdir(basedir)
    for pil in PILS:
        fn = f"{pil}_{ts:%Y%m%d}.txt"
        if not os.path.isfile(fn):
            pqstr = (
                f"data t {ts:%Y%m%d%H%M} text/noaaport/{fn} "
                f"text/noaaport/{fn} bogus"
            )
            subprocess.call(["pqinsert", "-i", "-p", pqstr, "/etc/fstab"])


if __name__ == "__main__":
    main(sys.argv)
