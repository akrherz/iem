"""Process a network's worth of ISD data, please

    python run_network_isd_ingest.py <network>
    ftp://ftp.ncdc.noaa.gov/pub/data/noaa
"""
from __future__ import print_function
import sys
import datetime
import subprocess

from pyiem.network import Table as NetworkTable


def build_xref():
    """Figure out how to reference stations"""
    xref = {}
    for linenum, line in enumerate(open("isd-history.txt")):
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
    xref = build_xref()
    nt = NetworkTable(network)
    for station in nt.sts:
        if nt.sts[station]["archive_begin"] is None:
            print("skipping %s as archive_begin is None" % (station,))
            continue
        eyear = nt.sts[station]["archive_begin"].year
        for option in xref.get(station, []):
            if option[2].year > eyear:
                print(
                    ("    skipping %s as data starts %s after station sts %s")
                    % (station, option[2].year, eyear)
                )
                continue
            if option[2].year == eyear:
                continue
            stid = station if len(station) == 4 else "K" + station
            cmd = ("python ingest_isd.py %s %s %s %s %s") % (
                option[0],
                option[1],
                stid,
                option[2].year,
                eyear,
            )
            print(cmd)
            subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main(sys.argv)
