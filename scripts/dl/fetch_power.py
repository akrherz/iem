"""Fetch the NASA POWER Dataset.

For now, we just run each Monday for the current year RUN_2AM.sh
"""
import sys
import time
import datetime
import subprocess

from tqdm import tqdm
import requests
import numpy as np
from pyiem import iemre
from pyiem.util import ncopen, logger, exponential_backoff

LOG = logger()


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    sts = datetime.date(year, 1, 1)
    ets = min([datetime.date(year, 12, 31), datetime.date.today()])
    current = {}
    now = ets
    while now >= sts:
        ds = iemre.get_grids(now, varnames="power_swdn")
        maxval = ds["power_swdn"].values.max()
        if np.isnan(maxval) or maxval < 0:
            LOG.info("adding %s as currently empty", now)
            current[now] = {"data": ds, "dirty": False}
        now -= datetime.timedelta(days=1)
    if not current:
        LOG.info("Nothing to be done...")
        return
    sts = min(list(current.keys()))
    ets = max(list(current.keys()))
    LOG.info("running between %s and %s", sts, ets)

    queue = []
    # 10x10 degree chunk is the max request size...
    for x0 in np.arange(iemre.WEST, iemre.EAST, 10.0):
        for y0 in np.arange(iemre.SOUTH, iemre.NORTH, 10.0):
            queue.append([x0, y0])
    for x0, y0 in tqdm(queue, disable=not sys.stdout.isatty()):
        url = (
            "https://power.larc.nasa.gov/api/temporal/daily/regional?"
            f"latitude-min={y0}&latitude-max={y0 + 9.9}&"
            f"longitude-min={x0}&"
            f"longitude-max={x0 + 9.9}&parameters=ALLSKY_SFC_SW_DWN&"
            f"community=SB&start={sts:%Y%m%d}&end={ets:%Y%m%d}&format=netcdf"
        )
        req = exponential_backoff(requests.get, url, timeout=60)
        # Can't find docs on how many requests/sec are allowed...
        if req is not None and req.status_code == 429:
            LOG.info("Got 429 (too-many-requests), sleeping 60")
            time.sleep(60)
            req = exponential_backoff(requests.get, url, timeout=60)
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
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fh.write(chunk)
        with ncopen(ncfn) as nc:
            for day, _ in enumerate(nc.variables["time"][:]):
                date = sts + datetime.timedelta(days=day)
                if date not in current:
                    continue
                # W/m2 to MJ/d 86400 / 1e6
                data = nc.variables["ALLSKY_SFC_SW_DWN"][day, :, :] * 0.0864
                # Sometimes there are missing values?
                if np.ma.is_masked(data):
                    data[data.mask] = np.mean(data)
                i, j = iemre.find_ij(x0, y0)
                # resample data is 0.5, iemre is 0.125
                data = np.repeat(np.repeat(data, 4, axis=0), 4, axis=1)
                data = np.where(data < 0, np.nan, data)
                shp = np.shape(data)
                jslice = slice(j, min([j + shp[0], iemre.NY]))
                islice = slice(i, min([i + shp[1], iemre.NX]))
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
                current[date]["data"]["power_swdn"].values[
                    jslice, islice
                ] = data
                current[date]["dirty"] = True
    for date, item in current.items():
        if not item["dirty"]:
            continue
        LOG.info("saving %s", date)
        iemre.set_grids(date, item["data"])
        subprocess.call(
            [
                "python",
                "../iemre/db_to_netcdf.py",
                f"{date:%Y}",
                f"{date:%m}",
                f"{date:%d}",
            ]
        )


if __name__ == "__main__":
    main(sys.argv)
