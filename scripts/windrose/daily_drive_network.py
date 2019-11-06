"""Search for a network to generate windroses for

Called from RUN_2AM.sh script
"""
import os
import subprocess
import stat
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger

LOG = logger()
CACHEDIR = "/mesonet/share/windrose/climate/yearly"


def do_network(network):
    """Process a network"""
    # Update the STS while we are at it, this will help the database get
    # stuff cached too
    if network.find("_ASOS") > 0:
        subprocess.call(
            "python ../dbutil/compute_asos_sts.py %s" % (network,), shell=True
        )
    if network.find("_DCP") > 0:
        subprocess.call(
            "python ../dbutil/compute_hads_sts.py %s" % (network,), shell=True
        )
    subprocess.call(
        "python drive_network_windrose.py %s" % (network,), shell=True
    )


def main():
    """Main"""
    now = datetime.datetime.now()
    with get_dbconn("mesosite") as pgconn:
        df = read_sql(
            """SELECT max(id) as station, network from stations
            WHERE (network ~* 'ASOS' or network = 'AWOS' or network ~* 'DCP')
            and online = 't' GROUP by network ORDER by random()""",
            pgconn,
            index_col="network",
        )
    for network, row in df.iterrows():
        station = row["station"]
        testfn = "%s/%s_yearly.png" % (CACHEDIR, station)
        if not os.path.isfile(testfn):
            LOG.info(
                "Driving network %s because no file for %s", network, station
            )
            do_network(network)
            break
        mtime = os.stat(testfn)[stat.ST_MTIME]
        age = float(now.strftime("%s")) - mtime
        # 250 days in seconds, enough to cover the number of networks
        if age < (250 * 24 * 60 * 60):
            continue
        LOG.info("Driving network %s because of age!", network)
        do_network(network)
        break


if __name__ == "__main__":
    main()
