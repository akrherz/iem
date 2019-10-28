"""
Drive a windrose for a given network and site
"""
from __future__ import print_function
import datetime
import sys

from pyiem.plot.use_agg import plt
from pyiem.network import Table as NetworkTable
from pyiem.windrose_utils import windrose


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

    fn = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (sid,)
    print("%4s %-20.20s -- YR" % (sid, nt.sts[sid]["name"]), end="")
    res = windrose(sid, database=database, sname=nt.sts[sid]["name"])
    res.savefig(fn)
    plt.close()
    for month in range(1, 13):
        fn = ("/mesonet/share/windrose/climate/monthly/%02i/%s_%s.png") % (
            month,
            sid,
            datetime.datetime(2000, month, 1).strftime("%b").lower(),
        )
        print(" %s" % (month,), end="")
        res = windrose(
            sid, months=(month,), database=database, sname=nt.sts[sid]["name"]
        )
        res.savefig(fn)
        plt.close()

    print()


if __name__ == "__main__":
    main()
