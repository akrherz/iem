"""
Merge hourly values.

Not called from anywhere as dataset does not update, yet.
"""
import datetime
import os
import subprocess

import numpy as np
import pandas as pd
from pyiem.iemre import hourly_offset
from pyiem.util import ncopen

XREF = {
    "T2": "tmpk",
    "TD2": "dwpk",
    "U10": "uwnd",
    "V10": "vwnd",
    "PREC_ACC_NC": "p01m",  # CU_PHYSICS=0, so it is all grid scale
    "ACETLSM": "evap",
    "TSLB": "soilt",
    "SMOIS": "soilm",
}
RDA = "https://data.rda.ucar.edu/ds559.0"


def process(valid):
    """Do great things for this country."""
    tidx = hourly_offset(valid)
    nc = ncopen(f"/mesonet/data/conus404/{valid:%Y}_hourly.nc", "a")

    # Find grid index of Ames, IA
    lat = nc.variables["lat"][:]
    lon = nc.variables["lon"][:]
    dist = ((lat - 42.03) ** 2 + (lon - -93.65) ** 2) ** 0.5
    j, i = np.unravel_index(np.argmin(dist), dist.shape)

    # Radiation is a delta, so we need the previous hour too
    prev = valid - datetime.timedelta(hours=1)
    prev_ncfn = f"wrf2d_d01_{prev:%Y-%m-%d_%H}:00:00.nc"
    if not os.path.isfile(prev_ncfn):
        wyr = prev.year if prev.month < 10 else prev.year + 1
        subprocess.call(["wget", f"{RDA}/wy{wyr}/{prev:%Y%m}/{prev_ncfn}"])

    ncfn = f"wrf2d_d01_{valid:%Y-%m-%d_%H}:00:00.nc"
    if not os.path.isfile(ncfn):
        wyr = valid.year if valid.month < 10 else valid.year + 1
        subprocess.call(["wget", f"{RDA}/wy{wyr}/{valid:%Y%m}/{ncfn}"])

    ncin = ncopen(ncfn)
    prev_ncin = ncopen(prev_ncfn)
    for invar, outvar in XREF.items():
        nc[outvar][tidx] = ncin[invar][:]
        if not outvar.startswith("soil"):
            print("Ames %s %.4f" % (outvar, nc[outvar][tidx, j, i]))

    # "ACSWDN": "rsds"
    # This is J m-2, so we need to convert to W m-2
    nc["rsds"][tidx] = (
        (ncin["ACSWDNB"][:] + ncin["I_ACSWDNB"][:] * 1e9)
        - (prev_ncin["ACSWDNB"][:] + prev_ncin["I_ACSWDNB"][:] * 1e9)
    ) / 3600.0
    print("Ames %s %.4f" % ("rsds", nc["rsds"][tidx, j, i]))

    ncin.close()
    nc.close()

    # Remove last hour file
    os.unlink(prev_ncfn)


def main():
    """Frontend."""
    for dt in pd.date_range("1980/01/01", "2022/01/01", freq="H", tz="UTC"):
        process(dt)


if __name__ == "__main__":
    main()
