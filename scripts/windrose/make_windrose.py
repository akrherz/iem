"""
Drive a windrose for a given network and site
"""
import datetime
import sys
import os

from pyiem.plot.use_agg import plt
from pyiem.network import Table as NetworkTable
from pyiem.windrose_utils import windrose

CACHE_DIR = "/mesonet/share/windrose"


def main():
    """Go Main"""
    net = sys.argv[1]
    nt = NetworkTable(net)
    sid = sys.argv[2]

    database = "asos"
    if net in ("KCCI", "KELO", "KIMT"):
        database = "snet"
    elif net in ("IA_RWIS",):
        database = "rwis"
    elif net in ("ISUSM",):
        database = "isuag"
    elif net.find("_DCP") > 0:
        database = "hads"

    mydir = "%s/%s/%s" % (CACHE_DIR, net, sid)
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    fn = "%s/%s_yearly.png" % (mydir, sid)
    res = windrose(sid, database=database, sname=nt.sts[sid]["name"])
    res.savefig(fn)
    plt.close()
    for month in range(1, 13):
        fn = ("%s/%s_%s.png") % (
            mydir,
            sid,
            datetime.datetime(2000, month, 1).strftime("%b").lower(),
        )
        res = windrose(
            sid, months=(month,), database=database, sname=nt.sts[sid]["name"]
        )
        res.savefig(fn)
        plt.close()


if __name__ == "__main__":
    main()
