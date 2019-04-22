"""Fetch the NASA POWER Dataset.

For now, we just run each Monday for the current year RUN_2AM.sh
"""
import sys
import datetime


from tqdm import tqdm
import requests
import numpy as np
from pyiem import iemre
from pyiem.util import ncopen


def main(argv):
    """Go Main Go."""
    year = int(argv[1])
    ets = min([datetime.date(year, 12, 31), datetime.date.today()])
    queue = []
    for x0 in np.arange(iemre.WEST, iemre.EAST, 5.):
        for y0 in np.arange(iemre.SOUTH, iemre.NORTH, 5.):
            queue.append([x0, y0])
    for x0, y0 in tqdm(queue, disable=not sys.stdout.isatty()):
        url = (
            "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py?"
            "request=execute&identifier=Regional&"
            "parameters=ALLSKY_SFC_SW_DWN&"
            "startDate=%s0101&endDate=%s&userCommunity=SSE&"
            "tempAverage=DAILY&bbox=%s,%s,%s,%s&user=anonymous&"
            "outputList=NETCDF"
        ) % (year, ets.strftime("%Y%m%d"), y0, x0,
             min([y0 + 5., iemre.NORTH]) - 0.1,
             min([x0 + 5., iemre.EAST]) - 0.1)
        req = requests.get(url, timeout=60)
        js = req.json()
        if 'outputs' not in js:
            print(url)
            print(js)
            continue
        fn = js['outputs']['netcdf']
        req = requests.get(fn, timeout=60, stream=True)
        ncfn = '/tmp/power%s.nc' % (year, )
        with open(ncfn, 'wb') as fh:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    fh.write(chunk)
            fh.close()
        nc = ncopen(ncfn)
        for day, _ in enumerate(nc.variables['time'][:]):
            date = datetime.date(year, 1, 1) + datetime.timedelta(days=day)
            # kwh to MJ/d  3600 * 1000 / 1e6
            data = nc.variables['ALLSKY_SFC_SW_DWN'][day, :, :] * 3.6
            i, j = iemre.find_ij(x0, y0)
            # resample data is 0.5, iemre is 0.125
            data = np.repeat(np.repeat(data, 4, axis=0), 4, axis=1)
            shp = np.shape(data)
            # print("i: %s j: %s shp: %s" % (i, j, shp))
            renc = ncopen(iemre.get_daily_ncname(year), 'a')
            renc.variables['power_swdn'][
                iemre.daily_offset(date),
                slice(j, j+shp[0]), slice(i, i+shp[1])
            ] = data
            renc.close()
        nc.close()


if __name__ == '__main__':
    main(sys.argv)
