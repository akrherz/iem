"""Fetch the NASA POWER Dataset.

For now, we just run each Monday for the current year RUN_2AM.sh
"""

import subprocess
import sys
import time
from datetime import date, timedelta

import click
import httpx
import numpy as np
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_grids, set_grids
from pyiem.util import exponential_backoff, logger, ncopen
from tqdm import tqdm

LOG = logger()


@click.command()
@click.option("--year", type=int, required=True)
@click.option("--domain", default="", type=str, help="IEMRE Domain")
def main(year: int, domain: str):
    """Go Main Go."""
    gridnav = get_nav("iemre", domain)
    sts = date(year, 1, 1)
    ets = min([date(year, 12, 31), date.today()])
    current = {}
    now = ets
    while now >= sts:
        ds = get_grids(now, varnames="power_swdn", domain=domain)
        maxval = ds["power_swdn"].values.max()
        if np.isnan(maxval) or maxval < 0:
            LOG.info("adding %s as currently empty", now)
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
        req = exponential_backoff(httpx.get, url, timeout=60)
        # Can't find docs on how many requests/sec are allowed...
        if req is not None and req.status_code == 429:
            LOG.info("Got 429 (too-many-requests), sleeping 60")
            time.sleep(60)
            req = exponential_backoff(httpx.get, url, timeout=60)
        if req is None or req.status_code != 200:
            LOG.warning(
                "failed to download %s with %s %s",
                url,
                "req is none" if req is None else req.status_code,
                "req is none" if req is None else req.text,
            )
            continue
        ncfn = f"/tmp/power{year}.nc"
        with open(ncfn, "wb") as fh:
            for chunk in req.iter_bytes(chunk_size=1024):
                if chunk:
                    fh.write(chunk)
        with ncopen(ncfn) as nc:
            for day, _ in enumerate(nc.variables["time"][:]):
                date = sts + timedelta(days=day)
                if date not in current:
                    continue
                # W/m2 to MJ/d 86400 / 1e6
                data = nc.variables["ALLSKY_SFC_SW_DWN"][day, :, :] * 0.0864
                # Sometimes there are missing values?
                if np.ma.is_masked(data):
                    data[data.mask] = np.mean(data)
                i, j = gridnav.find_ij(x0, y0)
                # resample data is 0.5, iemre is 0.125
                data = np.repeat(np.repeat(data, 4, axis=0), 4, axis=1)
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
                present = current[date]["data"]["power_swdn"].values[
                    jslice, islice
                ]
                if present.mean() == data.mean():
                    continue
                current[date]["data"]["power_swdn"].values[jslice, islice] = (
                    data
                )
                current[date]["dirty"] = True
    for date, item in current.items():
        if not item["dirty"]:
            continue
        LOG.info("saving %s", date)
        set_grids(date, item["data"], domain=domain)
        subprocess.call(
            [
                "python",
                "../iemre/db_to_netcdf.py",
                f"--date={date:%Y-%m-%d}",
                f"--domain={domain}",
            ]
        )


if __name__ == "__main__":
    main()
