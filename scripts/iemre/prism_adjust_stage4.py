"""So we are here, this is our life...

Take the PRISM data, valid at 12z and bias correct the hourly stage IV data

"""

import datetime
import os
import sys

import numpy as np
import pandas as pd
from pyiem import prism as prismutil
from pyiem.iemre import daily_offset, hourly_offset
from pyiem.util import find_ij, logger, ncopen, utc
from scipy.interpolate import NearestNDInterpolator

DEBUGLON = -93.89
DEBUGLAT = 42.04
LOG = logger()


def compute_s4total(valid):
    """Figure out the 24 hour total for this timestamp."""
    # Split into two, so to support 1 January without yucky code
    # 13z yesterday, arrears
    sts = valid - datetime.timedelta(hours=23)
    tidx0 = hourly_offset(sts)
    # 23z yesterday
    tidx1 = hourly_offset(sts + datetime.timedelta(hours=10))
    ncfn = f"/mesonet/data/stage4/{sts.year}_stage4_hourly.nc"
    stage4total = None
    if os.path.isfile(ncfn):
        with ncopen(ncfn) as nc:
            p01m = nc.variables["p01m"]
            LOG.info("%s [%s thru %s]", ncfn, tidx0, tidx1)
            stage4total = np.sum(p01m[tidx0 : (tidx1 + 1), :, :], axis=0)

    # 0z today
    sts = valid - datetime.timedelta(hours=12)
    tidx0 = hourly_offset(sts)
    # 11z today
    tidx1 = hourly_offset(valid)
    ncfn = f"/mesonet/data/stage4/{sts.year}_stage4_hourly.nc"
    with ncopen(ncfn) as nc:
        p01m = nc.variables["p01m"]
        LOG.info("%s [%s thru %s]", ncfn, tidx0, tidx1)
        tt = np.sum(p01m[tidx0 : (tidx1 + 1), :, :], axis=0)
        stage4total = tt if stage4total is None else (stage4total + tt)

    return stage4total


def workflow(valid):
    """Our workflow"""
    LOG.info("Processing %s", valid)
    # read prism
    tidx = daily_offset(valid)
    with ncopen(f"/mesonet/data/prism/{valid.year}_daily.nc", "r") as nc:
        ppt = nc.variables["ppt"][tidx, :, :]
        # missing as zero
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
    ppt = np.where(ppt.mask, 0, ppt)
    (lons, lats) = np.meshgrid(lons, lats)
    (pi, pj) = prismutil.find_ij(DEBUGLON, DEBUGLAT)
    LOG.info("prism debug point ppt: %.3f", ppt[pj, pi])

    s4total = compute_s4total(valid)
    with ncopen(f"/mesonet/data/stage4/{valid.year}_stage4_hourly.nc") as nc:
        s4lons = nc.variables["lon"][:]
        s4lats = nc.variables["lat"][:]
    sj, si = find_ij(s4lons, s4lats, DEBUGLON, DEBUGLAT)
    LOG.info(
        "stage4 s4total: %.3f lon: %.2f (%.2f) lat: %.2f (%.2f)",
        s4total[sj, si],
        s4lons[sj, si],
        DEBUGLON,
        s4lats[sj, si],
        DEBUGLAT,
    )
    # make sure the s4total does not have zeros
    s4total = np.where(s4total < 0.001, 0.001, s4total)

    nn = NearestNDInterpolator((lons.flatten(), lats.flatten()), ppt.flat)
    prism_on_s4grid = nn(s4lons, s4lats)
    multiplier = prism_on_s4grid / s4total
    LOG.info(
        "gridavgs: prism: %.3f stageIV: %.3f prismons4grid: %.3f mul: %.3f",
        np.mean(ppt),
        np.mean(s4total),
        np.mean(prism_on_s4grid),
        np.mean(multiplier),
    )
    LOG.info(
        "prism: %.3f stageIV: %.4f prismons4grid: %.3f mul: %.3f",
        ppt[pj, pi],
        s4total[sj, si],
        prism_on_s4grid[sj, si],
        multiplier[sj, si],
    )
    # 13 z yesterday
    sts = valid - datetime.timedelta(hours=23)
    # Through 12z file
    ets = valid
    for now in pd.date_range(sts, ets, freq="1h"):
        idx = hourly_offset(now)
        ncfn = f"/mesonet/data/stage4/{now.year}_stage4_hourly.nc"
        if not os.path.isfile(ncfn):
            continue
        with ncopen(ncfn, "a") as nc:
            oldval = nc.variables["p01m"][idx]
            # we threshold the s4total to at least 0.001,
            # so we divide by 24 here
            # and denote that if the multiplier is zero, then we net zero
            newval = np.where(oldval < 0.001, 0.00004, oldval) * multiplier
            # Unsure
            newval = np.where(newval < 0.01, 0, newval)
            nc.variables["p01m"][idx, :, :] = newval
            LOG.info(
                "adjust %s[%s] oldval: %.3f newval: %.3f",
                now.strftime("%Y%m%d%H"),
                idx,
                oldval[sj, si],
                newval[sj, si],
            )
            # make sure have data
            if np.ma.max(newval) > 0:
                nc.variables["p01m_status"][idx] = 3
            else:
                LOG.warning(
                    "NOOP for time %s[idx:%s]",
                    (
                        datetime.datetime(valid.year, 1, 1, 0)
                        + datetime.timedelta(hours=idx)
                    ).strftime("%Y-%m-%dT%H"),
                    idx,
                )


def main(argv):
    """Go Main"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), 12)
    workflow(valid)


if __name__ == "__main__":
    main(sys.argv)
