"""Ensure that our RTMA files have all we need.

Called from RUN_2AM.sh for 3 days ago.
"""
import os
import subprocess
import sys
import tempfile

import pygrib
import requests
from pyiem.util import logger, utc

LOG = logger()
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


def main(argv):
    """Run for a given date."""
    now = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    for hr in range(24):
        now = now.replace(hour=hr)
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/"
            "model/rtma/%H/rtma.t%Hz.awp2p5f000.grib2"
        )
        if not os.path.isfile(fn):
            jobs = list(WMO_XREF.keys())
        else:
            jobs = []
            grbs = pygrib.open(fn)
            for key, sn in GRIB_XREF.items():
                try:
                    grbs.select(shortName=sn)[0].values
                except Exception:
                    jobs.append(key)
            grbs.close()
        if jobs:
            LOG.warning("%s jobs %s", now, jobs)
        for key in jobs:
            url = (
                "https://www.ncei.noaa.gov/data/national-digital-guidance-"
                f"database/access/{'historical/' if now.year < 2020 else ''}"
                f"{now:%Y%m}/{now:%Y%m%d}/"
                f"{WMO_XREF[key]}_KWBR_{now:%Y%m%d%H%M}"
            )
            LOG.info("Downloading %s", url)
            req = requests.get(url, timeout=60)
            if req.status_code != 200:
                LOG.info("Failed to get %s got %s", url, req.status_code)
                continue
            # We need to inspect this file as we do not want the forecast
            # analysis error grib data, ie some of these files have 2 messages
            with tempfile.NamedTemporaryFile(delete=False) as fh:
                fh.write(req.content)
            try:
                grbs = pygrib.open(fh.name)
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
                grbs.close()
            except Exception:
                LOG.warning("%s not found in %s", key, fn)
            os.unlink(fh.name)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as _tmpdir:
        os.chdir(_tmpdir)
        main(sys.argv)
