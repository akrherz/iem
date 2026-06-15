"""Fetch the NASA POWER Dataset.

Based on present documentation that suggests ~4 day availability, but we have
found at least coarse resolution data at ~2 day availability.  This coarse
resolution data confuses the processing as we see there is data, but we don't
want it.  So we attempt to detect this by doing a unique values count.

The processing runs for the current year from RUN_2AM.sh and will attempt
to get whatever data it can find from the service.  We also force a
reprocessing for a 5 month old date, FWIW.
"""

import subprocess
import sys
import time
from datetime import date, datetime, timedelta

import click
import httpx
import numpy as np
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_grids, set_grids
from pyiem.util import exponential_backoff, logger, ncopen
from tqdm import tqdm

LOG = logger()


@click.command()
@click.option("--year", type=int, help="Year to Process")
@click.option("--date", "dt", type=click.DateTime(), help="Date to fetch")
@click.option("--domain", default="conus", type=str, help="IEMRE Domain")
@click.option("--force", is_flag=True, help="Force a re-download of data")
def main(year: int | None, dt: datetime | None, domain: str, force: bool):
    """Go Main Go."""
    gridnav = get_nav("iemre", domain)
    if dt is not None:
        sts = dt.date()
        ets = sts
    else:
        sts = date(year, 1, 1)
        ets = min([date(year, 12, 31), date.today()])
    current = {}
    now = ets
    while now >= sts:
        ds = get_grids(now, varnames="power_swdn", domain=domain)
        # A backhanded way to detect if we have all missing data or if we
        # have a very coarse resolution product currently saved.
        unique_count = len(np.unique(ds["power_swdn"].values))
        # 1_000 threshold was found to be noisey for winter months
        if force or unique_count < 500:
            LOG.info(
                "adding %s to queue because %s",
                now,
                "--force" if force else f"unique_count={unique_count}<500",
            )
            current[now] = {"data": ds, "dirty": False}
        now -= timedelta(days=1)
    if not current:
        LOG.info("Nothing to be done...")
        return
    sts = min(list(current.keys()))
    ets = max(list(current.keys()))
    LOG.info("running between %s and %s", sts, ets)

    queue = []
    # 10x10 degree chunk is the max request size...
    for x0 in np.arange(gridnav.left, gridnav.right, 10.0):
        for y0 in np.arange(gridnav.bottom, gridnav.top, 10.0):
            queue.append([x0, y0])  # noqa
    for x0, y0 in tqdm(queue, disable=not sys.stdout.isatty()):
        url = (
            "https://power.larc.nasa.gov/api/temporal/daily/regional?"
            f"latitude-min={y0}&latitude-max={y0 + 9.9}&"
            f"longitude-min={x0}&"
            f"longitude-max={x0 + 9.9}&parameters=ALLSKY_SFC_SW_DWN&"
            f"community=SB&start={sts:%Y%m%d}&end={ets:%Y%m%d}&format=netcdf"
        )
        resp = exponential_backoff(httpx.get, url, timeout=60)
        # Can't find docs on how many requests/sec are allowed...
        if resp is not None and resp.status_code == 429:
            LOG.info("Got 429 (too-many-requests), sleeping 60")
            time.sleep(60)
            resp = exponential_backoff(httpx.get, url, timeout=60)
        if resp is None or resp.status_code != 200:
            LOG.warning(
                "failed to download %s with %s %s",
                url,
                "resp is none" if resp is None else resp.status_code,
                "resp is none" if resp is None else resp.text,
            )
            continue
        ncfn = f"/tmp/power{year}_{domain}.nc"
        with open(ncfn, "wb") as fh:
            for chunk in resp.iter_bytes(chunk_size=1024):
                if chunk:
                    fh.write(chunk)
        with ncopen(ncfn) as nc:
            for day, _ in enumerate(nc.variables["time"][:]):
                dt = sts + timedelta(days=day)
                if dt not in current:
                    continue
                # W/m2 to MJ/d 86400 / 1e6
                data = nc.variables["ALLSKY_SFC_SW_DWN"][day] * 0.0864
                # Sometimes there are missing values?
                if np.ma.is_masked(data):
                    if data.mask.all():
                        LOG.info(
                            "[%s] Ignoring all masked values for %s %s",
                            domain,
                            dt,
                            (x0, y0),
                        )
                        continue
                    meanval = np.mean(data)
                    LOG.warning(
                        "[%s] Replacing %.1f%% masked values for %s "
                        "with mean %.2f for %.1f %.1f",
                        domain,
                        100.0 * np.sum(data.mask) / data.size,
                        dt,
                        meanval,
                        x0,
                        y0,
                    )
                    data = data.filled(meanval)
                i, j = gridnav.find_ij(x0, y0)
                # NASA Power is 1 degree for Solar, so repeat 8x
                data = np.repeat(np.repeat(data, 8, axis=0), 8, axis=1)
                data = np.where(data < 0, np.nan, data)
                shp = np.shape(data)
                jslice = slice(j, min([j + shp[0], gridnav.ny]))
                islice = slice(i, min([i + shp[1], gridnav.nx]))
                # align grids
                data = data[
                    slice(0, jslice.stop - jslice.start),
                    slice(0, islice.stop - islice.start),
                ]
                # get currentdata
                present = current[dt]["data"]["power_swdn"].values[
                    jslice, islice
                ]
                if present.mean() == data.mean():
                    continue
                current[dt]["data"]["power_swdn"].values[jslice, islice] = data
                current[dt]["dirty"] = True
    for _dt, item in current.items():
        if not item["dirty"]:
            continue
        LOG.info("saving %s", _dt)
        set_grids(_dt, item["data"], domain=domain)
        subprocess.call(
            [
                "python",
                "../iemre/db_to_netcdf.py",
                f"--date={_dt:%Y-%m-%d}",
                f"--domain={domain}",
                "--varname=power_swdn",
            ]
        )


if __name__ == "__main__":
    main()
