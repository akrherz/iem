"""Ensure that our RTMA files have all we need.

Called from RUN_2AM.sh for 3 days ago.
"""

import os
import subprocess
import tempfile
from datetime import datetime, timezone

import click
import httpx
import pygrib
from pyiem.util import archive_fetch, logger

LOG = logger()
ARCHIVE_SWITCH = datetime(2020, 5, 16, tzinfo=timezone.utc)
WMO_XREF = {
    "PRES": "LPIA98",
    "DPT": "LRIA98",
    "TMP": "LTIA98",
    "UGRD": "LUIA98",
    "VGRD": "LVIA98",
}
GRIB_XREF = {
    "TMP": "2t",
    "UGRD": "10u",
    "VGRD": "10v",
    "DPT": "2d",
    "PRES": "sp",
}


def workflow(now: datetime):
    """Run for a given date."""
    ppath = now.strftime("%Y/%m/%d/model/rtma/%H/rtma.t%Hz.awp2p5f000.grib2")
    with archive_fetch(ppath) as fn:
        if fn is None:
            jobs = list(WMO_XREF.keys())
        else:
            jobs = []
            with pygrib.open(fn) as grbs:
                for key, sn in GRIB_XREF.items():
                    try:
                        _ = grbs.select(
                            shortName=sn, typeOfGeneratingProcess=0
                        )[0].values
                    except Exception:
                        jobs.append(key)
    if jobs:
        LOG.warning("%s jobs %s", now, jobs)
    for key in jobs:
        url = (
            "https://www.ncei.noaa.gov/data/national-digital-guidance-"
            f"database/access/{'historical/' if now < ARCHIVE_SWITCH else ''}"
            f"{now:%Y%m}/{now:%Y%m%d}/"
            f"{WMO_XREF[key]}_KWBR_{now:%Y%m%d%H%M}"
        )
        LOG.info("Downloading %s", url)
        try:
            resp = httpx.get(url, timeout=60)
            resp.raise_for_status()
        except Exception as exp:
            LOG.info("Failed to get %s got %s", url, exp)
            continue
        # We need to inspect this file as we do not want the forecast
        # analysis error grib data, ie some of these files have 2 messages
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(resp.content)
        try:
            with pygrib.open(fh.name) as grbs:
                msgs = grbs.select(
                    shortName=GRIB_XREF[key],
                    typeOfGeneratingProcess=0,
                )
                if not msgs:
                    LOG.info("No %s found in %s", key, fh.name)
                    os.unlink(fh.name)
                    continue
                if grbs.messages > 1:
                    LOG.info("Found %s messages, trimming", grbs.messages)
                    with open(fh.name, "wb") as fh2:
                        fh2.write(msgs[0].tostring())
                # Caution, we don't use -i here as this name is not unique
                cmd = [
                    "pqinsert",
                    "-p",
                    f"data u {now:%Y%m%d%H%M} unused model/rtma/{now:%H}/"
                    f"rtma.t{now:%H}z.awp2p5f000.grib2 grib2",
                    fh.name,
                ]
                subprocess.call(cmd)
        except Exception:
            LOG.warning("%s not found in %s", key, fn)
        os.unlink(fh.name)


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), help="Specify UTC valid time"
)
def main(dt: datetime):
    """Go Main Go."""
    dt = dt.replace(tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory() as _tmpdir:
        os.chdir(_tmpdir)
        for hr in range(24):
            workflow(dt.replace(hour=hr))


if __name__ == "__main__":
    main()
