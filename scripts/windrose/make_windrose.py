"""
Drive a windrose for a given network and site
"""

import os
from calendar import month_abbr

import click
from pyiem.network import Table as NetworkTable
from pyiem.plot.use_agg import plt
from pyiem.windrose_utils import windrose

CACHE_DIR = "/mesonet/share/windrose"


@click.command()
@click.option("--network", required=True, help="Network Identifier")
@click.option("--station", required=True, help="Station Identifier")
def main(network, station):
    """Go Main"""
    nt = NetworkTable(network, only_online=False)

    database = "asos"
    if network in ("KCCI", "KELO", "KIMT"):
        database = "snet"
    elif network.find("_RWIS") > 0:
        database = "rwis"
    elif network in ("ISUSM",):
        database = "isuag"
    elif network.find("_DCP") > 0:
        database = "hads"

    mydir = os.path.join(CACHE_DIR, network, station)
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    fn = f"{mydir}/{station}_yearly.png"
    res = windrose(
        station,
        database=database,
        sname=nt.sts[station]["name"],
        tzname=nt.sts[station]["tzname"],
    )
    res.savefig(fn)
    plt.close()
    for month in range(1, 13):
        fn = f"{mydir}/{station}_{month_abbr[month].lower()}.png"
        res = windrose(
            station,
            months=[
                month,
            ],
            database=database,
            sname=nt.sts[station]["name"],
            tzname=nt.sts[station]["tzname"],
        )
        res.savefig(fn)
        plt.close()


if __name__ == "__main__":
    main()
