"""Process a network's worth of ISD data, please

    python run_network_isd_ingest.py <network> <lastyr_exclusive>
    ftp://ftp.ncdc.noaa.gov/pub/data/noaa
"""
import sys
import datetime
import subprocess

from pyiem.util import logger
from pyiem.network import Table as NetworkTable

LOG = logger()


def build_xref():
    """Figure out how to reference stations"""
    xref = {}
    with open("isd-history.txt", encoding="utf-8") as fh:
        for linenum, line in enumerate(fh):
            if linenum < 24:
                continue
            airforce = line[:6]
            wban = int(line[7:12])
            faa = line[51:55]
            if faa.strip() == "":
                continue
            if faa[0] == "K":
                faa = faa[1:]
            sts = datetime.datetime.strptime(line[82:90], "%Y%m%d")
            ets = datetime.datetime.strptime(line[91:99], "%Y%m%d")
            ar = xref.setdefault(faa, [])
            ar.append([airforce, wban, sts, ets])
    return xref


def main(argv):
    """Go Main Go"""
    network = argv[1]
    till_year = int(argv[2])
    xref = build_xref()
    nt = NetworkTable(network, only_online=False)
    for station in nt.sts:
        if nt.sts[station]["archive_begin"] is None:
            LOG.info("skipping %s as archive_begin is None", station)
            continue
        # Loop over any matching stations above
        for option in xref.get(station, []):
            if option[2].year >= till_year:
                LOG.info(
                    "skipping %s:%s as starts after %s",
                    station,
                    option,
                    till_year,
                )
                continue
            stid = station if len(station) == 4 else "K" + station
            eyear = min([till_year, option[3].year])
            cmd = [
                "python",
                "ingest_isd.py",
                option[0],
                option[1],
                stid,
                str(option[2].year),
                str(eyear),
            ]
            LOG.info(" ".join(cmd))
            subprocess.call(cmd)


if __name__ == "__main__":
    main(sys.argv)
