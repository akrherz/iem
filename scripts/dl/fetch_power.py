"""Fetch the NASA POWER Dataset.

For now, we just run each Monday for the current year RUN_2AM.sh
"""
import sys
import datetime
import subprocess

from tqdm import tqdm
import requests
import numpy as np
from pyiem import iemre
from pyiem.util import ncopen, logger


def main(argv):
    """Go Main Go."""
    log = logger()
    year = int(argv[1])
    sts = datetime.date(year, 1, 1)
    ets = min([datetime.date(year, 12, 31), datetime.date.today()])
    current = {}
    now = ets
    while now >= sts:
        ds = iemre.get_grids(now, varnames="power_swdn")
        maxval = ds["power_swdn"].values.max()
        if np.isnan(maxval) or maxval < 0:
            log.debug("adding %s as currently empty", now)
            current[now] = {"data": ds, "dirty": False}
        now -= datetime.timedelta(days=1)
    sts = min(list(current.keys()))
    ets = max(list(current.keys()))
    log.debug("running between %s and %s", sts, ets)

    queue = []
    for x0 in np.arange(iemre.WEST, iemre.EAST, 5.0):
        for y0 in np.arange(iemre.SOUTH, iemre.NORTH, 5.0):
            queue.append([x0, y0])
    for x0, y0 in tqdm(queue, disable=not sys.stdout.isatty()):
        url = (
            "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?"
            "request=execute&identifier=Regional&"
            "parameters=ALLSKY_SFC_SW_DWN&"
            "startDate=%s&endDate=%s&userCommunity=SSE&"
            "tempAverage=DAILY&bbox=%s,%s,%s,%s&user=anonymous&"
            "outputList=NETCDF"
        ) % (
            sts.strftime("%Y%m%d"),
            ets.strftime("%Y%m%d"),
            y0,
            x0,
            min([y0 + 5.0, iemre.NORTH]) - 0.1,
            min([x0 + 5.0, iemre.EAST]) - 0.1,
        )
        req = requests.get(url, timeout=60)
        js = req.json()
        if "outputs" not in js:
            print(url)
            print(js)
            continue
        fn = js["outputs"]["netcdf"]
        req = requests.get(fn, timeout=60, stream=True)
        ncfn = "/tmp/power%s.nc" % (year,)
        with open(ncfn, "wb") as fh:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fh.write(chunk)
            fh.close()
        with ncopen(ncfn) as nc:
            for day, _ in enumerate(nc.variables["time"][:]):
                date = sts + datetime.timedelta(days=day)
                if date not in current:
                    continue
                # kwh to MJ/d  3600 * 1000 / 1e6
                data = nc.variables["ALLSKY_SFC_SW_DWN"][day, :, :] * 3.6
                # Sometimes there are missing values?
                if np.ma.is_masked(data):
                    data[data.mask] = np.mean(data)
                i, j = iemre.find_ij(x0, y0)
                # resample data is 0.5, iemre is 0.125
                data = np.repeat(np.repeat(data, 4, axis=0), 4, axis=1)
                data = np.where(data < 0, np.nan, data)
                shp = np.shape(data)
                jslice = slice(j, j + shp[0])
                islice = slice(i, i + shp[1])
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
    for date in current:
        if not current[date]["dirty"]:
            continue
        log.debug("saving %s", date)
        iemre.set_grids(date, current[date]["data"])
        subprocess.call(
            "python ../iemre/db_to_netcdf.py %s"
            % (date.strftime("%Y %m %d"),),
            shell=True,
        )


if __name__ == "__main__":
    main(sys.argv)
