"""
Merge hourly values.

Not called from anywhere as dataset does not update, yet.
"""
import sys

from pyiem.iemre import hourly_offset
from pyiem.util import ncopen, utc

XREF = {
    "T2": "tmpk",
    "TD2": "dwpk",
    "U10": "uwnd",
    "V10": "vwnd",
    "PREC_ACC_NC": "p01m",  # doubt this is right
    "ACETLSM": "evap",
    "ACSWDN": "rsds",  # doubt this too, likely after canopy
    "TSLB": "soilt",
    "SMOIS": "soilm",
}


def main(argv):
    """Do great things for this country."""
    valid = utc(*[int(a) for a in argv[1:]])
    tidx = hourly_offset(valid)
    nc = ncopen(f"/mesonet/data/conus404/{valid:%Y}_hourly.nc", "a")

    ncin = ncopen("wrf2d_d01_1979-10-01_00:00:00.nc")
    for invar, outvar in XREF.items():
        nc[outvar][tidx] = ncin[invar][:]

    ncin.close()
    nc.close()


if __name__ == "__main__":
    main(sys.argv)
