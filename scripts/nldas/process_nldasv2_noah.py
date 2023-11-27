"""Download NLDASv2 data from NASA.

NOTE: Local ~/.netrc file must be configured with NASA Earthdata credentials.

Run from RUN_0Z.sh for 5 day old data.
"""
import os
import subprocess
import sys

import pygrib
from pyiem.iemre import hourly_offset
from pyiem.util import ncopen, utc

SOIL_LEVELS = {
    "0-10 cm down": 0,
    "10-40 cm down": 1,
    "40-100 cm down": 2,
    "100-200 cm down": 3,
}
DEPTHS = {
    "0-10 cm down": 100.0,
    "10-40 cm down": 300.0,
    "40-100 cm down": 600.0,
    "100-200 cm down": 1000.0,
}
VAL2NC = {
    "TSOIL": "soilt",
    "SOILM": "soilm",
}


def process(valid):
    """Run for the given UTC timestamp."""
    fn = f"nldas.{valid:%Y%m%d%H}"
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
        f"NLDAS_NOAH0125_H.002/2023/{valid:%03j}/NLDAS_NOAH0125_H."
        f"A{valid:%Y%m%d}.{valid:%H}00.002.grb",
    ]
    if not os.path.isfile(fn):
        subprocess.call(cmd)
    # pygrib can't deal with this grib1 file, so we have to hack away here
    with subprocess.Popen(["wgrib", fn], stdout=subprocess.PIPE) as proc:
        content = proc.stdout.read().decode("utf-8")
    grbs = pygrib.open(fn)
    idx = hourly_offset(valid)
    for line in content.split("\n"):
        tokens = line.split(":")
        if len(tokens) < 11:
            continue
        if tokens[3] not in ["TSOIL", "SOILM"]:
            continue
        if tokens[11] not in SOIL_LEVELS:
            continue
        grb = grbs[int(tokens[0])]
        if tokens[3] == "SOILM":
            vals = grb.values / DEPTHS[tokens[11]]
        else:
            vals = grb.values
        with ncopen(f"/mesonet/data/nldas/{valid:%Y}_hourly.nc", "a") as nc:
            nc.variables[VAL2NC[tokens[3]]][
                idx, SOIL_LEVELS[tokens[11]]
            ] = vals
    os.unlink(fn)


def main(argv):
    """Run for a given UTC date."""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]))
    for hr in range(1):
        process(valid.replace(hour=hr))


if __name__ == "__main__":
    main(sys.argv)
