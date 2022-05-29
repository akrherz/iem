"""Ensure that our RTMA files have all we need."""
import os
import sys

import pygrib
import requests
from pyiem.util import utc, logger

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
        basedir = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/model/rtma/%H/")
        if not os.path.isdir(basedir):
            LOG.info("Creating %s", basedir)
            os.makedirs(basedir)
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
            LOG.info("%s jobs %s", now, jobs)
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
            with open("tmp.grb", "wb") as fh:
                fh.write(req.content)
            grbs = pygrib.open("tmp.grb")
            try:
                grb = grbs.select(
                    shortName=GRIB_XREF[key],
                    typeOfGeneratingProcess=0,
                )[0]
                with open(fn, "ab") as fh:
                    fh.write(grb.tostring())
            except Exception:
                LOG.warning("%s not found in %s", key, fn)
            grbs.close()


if __name__ == "__main__":
    main(sys.argv)
