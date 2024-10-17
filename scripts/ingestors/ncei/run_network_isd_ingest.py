"""Process a network's worth of ISD data, please."""

import subprocess
from datetime import datetime

import click
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

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
            sts = datetime.strptime(line[82:90], "%Y%m%d")
            ets = datetime.strptime(line[91:99], "%Y%m%d")
            ar = xref.setdefault(faa, [])
            ar.append([airforce, wban, sts, ets])
    return xref


@click.command()
@click.option("--network", help="Network Identifier", required=True)
@click.option("--till_year", help="Year to stop at", required=True, type=int)
def main(network: str, till_year: int):
    """Go Main Go"""
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
                "--airforce",
                str(option[0]),
                "--wban",
                str(option[1]),
                "--faa",
                stid,
                "--year1",
                "1998",
                "--year2",
                f"{eyear}",
            ]
            LOG.info(" ".join(cmd))
            subprocess.call(cmd)


if __name__ == "__main__":
    main()
