"""Generate a windrose for each site in the specified network..."""
import subprocess
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def main(argv):
    """Go Main"""
    net = argv[1]
    nt = NetworkTable(net)
    for sid in nt.sts:
        LOG.info("calling make_windrose.py network: %s sid: %s", net, sid)
        subprocess.call(["python", "make_windrose.py", net, sid])


if __name__ == "__main__":
    main(sys.argv)
