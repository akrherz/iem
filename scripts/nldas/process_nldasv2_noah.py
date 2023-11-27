"""Download NLDASv2 data from NASA.

NOTE: Local ~/.netrc file must be configured with NASA Earthdata credentials.

Run from RUN_0Z.sh for 5 day old data.
"""
import os
import subprocess
import sys

from pyiem.iemre import hourly_offset
from pyiem.util import ncopen, utc


def process(valid):
    """Run for the given UTC timestamp."""
    fn = f"nldas.{valid:%Y%m%d%H}.nc"
    cmd = [
        "wget",
        "-q",
        "--load-cookies",
        "~/.urs_cookies",
        "--save-cookies",
        "~/.urs_cookies",
        "--keep-session-cookies",
        "-O",
        fn,
        "https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/"
        f"NLDAS_NOAH0125_H.2.0/{valid:%Y}/{valid:%03j}/NLDAS_NOAH0125_H."
        f"A{valid:%Y%m%d}.{valid:%H}00.020.nc",
    ]
    if not os.path.isfile(fn):
        subprocess.call(cmd)
    idx = hourly_offset(valid)
    SOILTVARS = [
        "SoilT_0_10cm",
        "SoilT_10_40cm",
        "SoilT_40_100cm",
        "SoilT_100_200cm",
    ]
    DEPTH_MM = [100.0, 300.0, 600.0, 1000.0]
    with ncopen(fn) as ncin, ncopen(
        f"/mesonet/data/nldas/{valid:%Y}_hourly.nc", "a"
    ) as ncout:
        for i, ncvar in enumerate(SOILTVARS):
            ncout.variables["soilt"][idx, i] = ncin.variables[ncvar][0]
            # mm over depth, we want fraction
            ncinv = ncvar.replace("SoilT", "SoilM")
            ncout.variables["soilm"][idx, i] = (
                ncin.variables[ncinv][0] / DEPTH_MM[i]
            )

    os.unlink(fn)


def main(argv):
    """Run for a given UTC date."""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    for hr in range(24):
        process(valid.replace(hour=hr))


if __name__ == "__main__":
    main(sys.argv)
