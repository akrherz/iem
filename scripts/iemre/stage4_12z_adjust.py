"""Use the QC'd 12z 24 Hour files to adjust hourly data.

No need to run for previous days as PRISM is available.

Called from:
  RUN_NOON.sh and RUN_0Z.sh for today.
"""

import datetime
import os

import click
import numpy as np
import pygrib
from pyiem import iemre
from pyiem.util import archive_fetch, logger, ncopen, utc

LOG = logger()


def save12z(ts, val):
    """Save the data to our daily 12z file."""
    ncfn = f"/mesonet/data/stage4/{ts.year}_stage4_daily.nc"
    if not os.path.isfile(ncfn):
        LOG.warning("File not found! %s", ncfn)
        return
    idx = iemre.daily_offset(ts)
    LOG.info("Writing 12z grid to %s at idx: %s", ncfn, idx)
    with ncopen(ncfn, "a") as nc:
        # Account for pre-2002 shape difference
        if val.shape == (880, 1160):
            nc.variables["p01d_12z"][idx, 1:, :] = val[:, 39:]
        else:
            nc.variables["p01d_12z"][idx] = val


def merge(ts):
    """
    Process an hour's worth of stage4 data into the hourly RE
    """

    # Load up the 12z 24h total, this is what we base our deltas on
    ppath = f"{ts:%Y/%m/%d}/stage4/ST4.{ts:%Y%m%d%H}.24h.grib"
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.info("stage4_12z_adjust %s is missing", ppath)
            return
        grbs = pygrib.open(fn)
        grb = grbs[1]
        val = grb.values
        grbs.close()
    save12z(ts, val)

    # storage is in the arrears
    sts = ts - datetime.timedelta(hours=23)
    pairs = [(sts, ts)]
    if ts.month == 1 and ts.day == 1:
        pairs = [
            (sts, sts + datetime.timedelta(hours=10)),  # 13z thr 23z
            (ts.replace(hour=0), ts),
        ]
    hourly_total = None
    for pair in pairs:
        ncfn = f"/mesonet/data/stage4/{pair[0].year}_stage4_hourly.nc"
        idx0 = iemre.hourly_offset(pair[0])
        idx1 = iemre.hourly_offset(pair[1])
        LOG.info("%s [%s thru %s]", ncfn, idx0, idx1)
        with ncopen(ncfn, timeout=60) as nc:
            # Check that the status value is (1,2), otherwise prism ran
            sentinel = np.nanmax(
                nc.variables["p01m_status"][idx0 : (idx1 + 1)]
            )
            if sentinel == 3:
                LOG.warning("Aborting as p01m_status[%s] == 3", sentinel)
                return
            p01m = nc.variables["p01m"]
            total = np.nansum(p01m[idx0 : (idx1 + 1)], axis=0)
            if hourly_total is None:
                hourly_total = total
            else:
                hourly_total = np.nansum([total, hourly_total], axis=0)
    # Set a min value to prevent div by zero
    hourly_total = np.where(hourly_total > 0.0, hourly_total, 0.00024)
    multiplier = val / hourly_total
    for pair in pairs:
        ncfn = f"/mesonet/data/stage4/{pair[0].year}_stage4_hourly.nc"
        idx0 = iemre.hourly_offset(pair[0])
        idx1 = iemre.hourly_offset(pair[1])
        with ncopen(ncfn, mode="a", timeout=60) as nc:
            nc.variables["p01m_status"][idx0 : (idx1 + 1)] = 2
            for idx in range(idx0, idx1 + 1):
                data = nc.variables["p01m"][idx, :, :]
                adjust = np.where(data > 0, data, 0.00001) * multiplier
                adjust = np.where(adjust > 250.0, 0, adjust)
                LOG.info(
                    "idx: %s orig:%.2f new:%.2f",
                    idx,
                    np.nanmean(data),
                    np.nanmean(adjust),
                )
                nc.variables["p01m"][idx, :, :] = np.where(
                    adjust < 0.01, 0, adjust
                )


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime.datetime):
    """Go Main Go"""
    merge(utc(dt.year, dt.month, dt.day, 12))


if __name__ == "__main__":
    main()
