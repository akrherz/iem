"""Fetch me the NARR

Appears that data for the previous month is available by the 9th of current mon

called from RUN_2AM.sh
"""

import glob
import os
import subprocess
from datetime import date, datetime, timedelta

import click
import pygrib
import requests
from pyiem.util import exponential_backoff, logger

LOG = logger()
TMP = "/mesonet/tmp"


def process(tarfn):
    """Process this tarfn"""
    os.chdir(TMP)
    subprocess.call(["tar", "-xf", tarfn])
    for grbfn in glob.glob("merged_AWIP32*sfc"):
        grbs = pygrib.open(grbfn)
        # NB: this sfc file has two DSWRF fields, one is a 3 hour average and
        # the other is a instantaneous forecast, we want the average!
        radgrb = grbs.select(parameterName="204", stepType="avg")[0]
        pcpgrb = grbs.select(parameterName="61")[0]

        dt = radgrb["dataDate"]
        hr = int(radgrb["dataTime"]) / 100.0
        ts = datetime.strptime(f"{dt} {hr:.0f}", "%Y%m%d %H")
        for prefix, grb in zip(["rad", "apcp"], [radgrb, pcpgrb]):
            fn = f"{prefix}_{ts:%Y%m%d%H%M}.grib"
            with open(fn, "wb") as fh:
                fh.write(grb.tostring())
            pqstr = (
                f"data a {ts:%Y%m%d%H%M} bogus "
                f"model/NARR/{prefix}_{ts:%Y%m%d%H%M}.grib grib"
            )
            subprocess.call(["pqinsert", "-p", pqstr, fn])
            LOG.info("grbfn: %s fn: %s", grbfn, fn)
            os.remove(fn)
        os.remove(grbfn)


def fetch_rda(year, month):
    """Get data please from RDA"""
    days = ["0109", "1019"]
    lastday = (date(year, month, 1) + timedelta(days=35)).replace(
        day=1
    ) - timedelta(days=1)
    days.append(f"20{lastday.day}")
    for day in days:
        uri = (
            "https://data.rda.ucar.edu/ds608.0/3HRLY/"
            f"{year}/NARRsfc_{year}{month:02.0f}_{day}.tar"
        )
        req = exponential_backoff(requests.get, uri, timeout=30, stream=True)
        tmpfn = f"{TMP}/narr.tar"
        with open(tmpfn, "wb") as fh:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fh.write(chunk)
        process(tmpfn)
        os.unlink(tmpfn)

    # Now call coop script
    subprocess.call(
        [
            "python",
            "/opt/iem/scripts/climodat/narr_solarrad.py",
            f"--year={year}",
            f"--month={month}",
        ]
    )
    subprocess.call(
        [
            "python",
            "/opt/iem/scripts/iemre/merge_narr.py",
            f"--year={year}",
            f"--month={month}",
        ]
    )


@click.command()
@click.option("--year", type=int, required=True)
@click.option("--month", type=int, required=True)
def main(year: int, month: int):
    """Go Main Go"""
    fetch_rda(year, month)


if __name__ == "__main__":
    main()
