"""So we are here, this is our life...

Take the PRISM data, valid at 12z and bias correct the hourly stage IV data

RUN_NOON.sh for 1 day ago
"""

import os
from datetime import datetime, timedelta

import click
import numpy as np
import pandas as pd
from pyiem import prism as prismutil
from pyiem import stage4 as stage4util
from pyiem.iemre import daily_offset, hourly_offset
from pyiem.util import logger, ncopen, utc
from rasterio.warp import reproject

DEBUGLON = -93.89
DEBUGLAT = 42.04
LOG = logger()


def compute_s4total(valid: datetime):
    """Figure out the 24 hour total for this timestamp."""
    # Split into two, so to support 1 January without yucky code
    # 13z yesterday, arrears
    sts = valid - timedelta(hours=23)
    tidx0 = hourly_offset(sts)
    # 23z yesterday
    tidx1 = hourly_offset(sts + timedelta(hours=10))
    ncfn = f"/mesonet/data/stage4/{sts.year}_stage4_hourly.nc"
    stage4total = None
    if os.path.isfile(ncfn):
        with ncopen(ncfn) as nc:
            p01m = nc.variables["p01m"]
            LOG.info("%s [%s thru %s]", ncfn, tidx0, tidx1)
            stage4total = np.sum(p01m[tidx0 : (tidx1 + 1), :, :], axis=0)

    # 0z today
    sts = valid - timedelta(hours=12)
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


def workflow(valid: datetime):
    """Our workflow"""
    LOG.info("Processing %s", valid)
    # read prism
    tidx = daily_offset(valid)
    with ncopen(f"/mesonet/data/prism/{valid.year}_daily.nc", "r") as nc:
        # rasterio freaks out if we have masked arrays
        ppt = nc.variables["ppt"][tidx].filled(0)
    (pi, pj) = prismutil.find_ij(DEBUGLON, DEBUGLAT)

    s4total = compute_s4total(valid)
    (si, sj) = stage4util.find_ij(DEBUGLON, DEBUGLAT)
    # make sure the s4total does not have zeros
    s4total = np.where(s4total < 0.001, 0.001, s4total)

    # reproject prism onto the stage4 grid
    prism_on_s4grid = np.zeros_like(s4total)
    reproject(
        ppt,
        prism_on_s4grid,
        src_transform=prismutil.AFFINE_NC,
        src_crs="EPSG:4326",
        dst_transform=stage4util.AFFINE_NC,
        dst_crs=stage4util.PROJPARMS,
        dst_nodata=0,
    )

    multiplier = prism_on_s4grid / s4total
    LOG.info(
        "DEBUGPT prism: %.3f s4total: %.3f prism_on_s4grid: %.3f mul: %.3f",
        ppt[pj, pi],
        s4total[sj, si],
        prism_on_s4grid[sj, si],
        multiplier[sj, si],
    )
    LOG.info(
        "gridavgs: prism: %.3f stageIV: %.3f prism_on_s4grid: %.3f mul: %.3f",
        np.mean(ppt),
        np.mean(s4total),
        np.mean(prism_on_s4grid),
        np.mean(multiplier),
    )
    # 13 z yesterday
    sts = valid - timedelta(hours=23)
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
                "adjust %s[%s] DEBUGPT: oldval: %.3f newval: %.3f",
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
                    "Not setting p01m_status due to zeroes for %s[idx:%s]",
                    (
                        datetime(valid.year, 1, 1, 0) + timedelta(hours=idx)
                    ).strftime("%Y-%m-%dT%H"),
                    idx,
                )


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Go Main"""
    workflow(utc(dt.year, dt.month, dt.day, 12))


if __name__ == "__main__":
    main()
