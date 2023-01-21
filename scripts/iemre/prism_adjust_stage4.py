"""So we are here, this is our life...

Take the PRISM data, valid at 12z and bias correct the hourly stage IV data

"""
import sys
import datetime

import numpy as np
from scipy.interpolate import NearestNDInterpolator
from pyiem.iemre import daily_offset, hourly_offset
from pyiem import prism as prismutil
from pyiem.util import utc, ncopen, find_ij, logger

DEBUGLON = -93.89
DEBUGLAT = 42.04
LOG = logger()


def workflow(valid):
    """Our workflow"""
    LOG.info("Processing %s", valid)
    if valid.month == 1 and valid.day == 1:
        LOG.warning("sorry Jan 1 processing is a TODO!")
        return
    # read prism
    tidx = daily_offset(valid)
    with ncopen(f"/mesonet/data/prism/{valid.year}_daily.nc", "r") as nc:
        ppt = nc.variables["ppt"][tidx, :, :]
        # missing as zero
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
    ppt = np.where(ppt.mask, 0, ppt)
    (lons, lats) = np.meshgrid(lons, lats)
    (i, j) = prismutil.find_ij(DEBUGLON, DEBUGLAT)
    LOG.info("prism debug point ppt: %.3f", ppt[j, i])

    # Interpolate this onto the stage4 grid
    nc = ncopen(
        f"/mesonet/data/stage4/{valid.year}_stage4_hourly.nc",
        "a",
        timeout=300,
    )
    p01m = nc.variables["p01m"]
    p01m_status = nc.variables["p01m_status"]
    s4lons = nc.variables["lon"][:]
    s4lats = nc.variables["lat"][:]
    i, j = find_ij(s4lons, s4lats, DEBUGLON, DEBUGLAT)
    # Values are in the hourly arrears, so start at -23 and thru current hour
    sts_tidx = hourly_offset(valid - datetime.timedelta(hours=23))
    ets_tidx = hourly_offset(valid + datetime.timedelta(hours=1))
    s4total = np.sum(p01m[sts_tidx:ets_tidx, :, :], axis=0)
    LOG.info(
        "stage4 s4total: %.3f lon: %.2f (%.2f) lat: %.2f (%.2f)",
        s4total[i, j],
        s4lons[i, j],
        DEBUGLON,
        s4lats[i, j],
        DEBUGLAT,
    )
    # make sure the s4total does not have zeros
    s4total = np.where(s4total < 0.001, 0.001, s4total)

    nn = NearestNDInterpolator((lons.flatten(), lats.flatten()), ppt.flat)
    prism_on_s4grid = nn(s4lons, s4lats)
    LOG.info(
        "shape of prism_on_s4grid: %s s4lons: %s ll: %.2f s4lats: %s ll: %.2f",
        np.shape(prism_on_s4grid),
        np.shape(s4lons),
        s4lons[0, 0],
        np.shape(s4lats),
        s4lats[0, 0],
    )
    multiplier = prism_on_s4grid / s4total
    LOG.info(
        "prism avg: %.3f stageIV avg: %.3f prismons4grid avg: %.3f mul: %.3f",
        np.mean(ppt),
        np.mean(s4total),
        np.mean(prism_on_s4grid),
        np.mean(multiplier),
    )
    LOG.info(
        "Boone IA0807 prism: %.3f stageIV: %.4f prismons4grid: %.3f mul: %.3f",
        ppt[431, 746],
        s4total[i, j],
        prism_on_s4grid[i, j],
        multiplier[i, j],
    )

    # Do the work now, we should not have to worry about the scale factor
    for tidx in range(sts_tidx, ets_tidx):
        oldval = p01m[tidx, :, :]
        # we threshold the s4total to at least 0.001, so we divide by 24 here
        # and denote that if the multiplier is zero, then we net zero
        newval = np.where(oldval < 0.001, 0.00004, oldval) * multiplier
        nc.variables["p01m"][tidx, :, :] = newval
        LOG.info(
            "adjust tidx: %s oldval: %.3f newval: %.3f",
            tidx,
            oldval[i, j],
            newval[i, j],
        )
        # make sure have data
        if np.ma.max(newval) > 0:
            p01m_status[tidx] = 2
        else:
            LOG.warning(
                "NOOP for time %s[idx:%s]",
                (
                    datetime.datetime(valid.year, 1, 1, 0)
                    + datetime.timedelta(hours=tidx)
                ).strftime("%Y-%m-%dT%H"),
                tidx,
            )
    nc.close()


def main(argv):
    """Go Main"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), 12)
    workflow(valid)


if __name__ == "__main__":
    main(sys.argv)
