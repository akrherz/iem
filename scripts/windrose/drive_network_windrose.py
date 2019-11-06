"""Generate a windrose for each site in the specified network...
"""
import sys
import subprocess

from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


def main(argv):
    """Go Main"""
    net = argv[1]
    nt = NetworkTable(net)
    for sid in nt.sts:
        LOG.info("calling make_windrose.py network: %s sid: %s", net, sid)
        subprocess.call(
            "python make_windrose.py %s %s" % (net, sid), shell=True
        )


if __name__ == "__main__":
    main(sys.argv)
