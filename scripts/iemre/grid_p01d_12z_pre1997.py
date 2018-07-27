"""Make a gridded analysis of p01d_12z based on obs."""
import sys
import datetime

import numpy as np
from metpy.units import units as mpunits
from metpy.units import masked_array
from metpy.gridding.interpolation import inverse_distance
from pandas.io.sql import read_sql
from pyiem.iemre import get_daily_ncname, daily_offset
from pyiem.util import ncopen, get_dbconn


def generic_gridder(day, nc, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    domain = nc.variables['hasdata'][:, :]
    xi, yi = np.meshgrid(nc.variables['lon'][:], nc.variables['lat'][:])
    res = np.ones(xi.shape) * np.nan
    # set a sentinel of where we won't be estimating
    res = np.where(domain > 0, res, -9999)
    # do our gridding
    grid = inverse_distance(df['lon'].values, df['lat'].values,
                            df[idx].values, xi, yi, 0.5)
    # replace nan values in res with whatever now is in grid
    res = np.where(np.isnan(res), grid, res)
    # replace sentinel back to np.nan
    res = np.where(res == -9999, np.nan, res)
    print(("%s %s rows for %s column min:%.3f max:%.3f"
           ) % (day, len(df.index), idx, np.nanmin(res), np.nanmax(res)))
    return masked_array(np.ma.array(res, mask=np.isnan(res)), mpunits('inch'))


def main(argv):
    """Do work please"""
    day = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    pgconn = get_dbconn('coop')
    df = read_sql("""
        SELECT a.precip, st_x(t.geom) as lon, st_y(t.geom) as lat
        from alldata a JOIN stations t ON (a.station = t.id)
        WHERE a.day = %s and t.network ~* 'CLIMATE' and
        substr(a.station,3,4) != '0000' and substr(station,3,1) != 'C'
        and precip >= 0 and precip < 50
    """, pgconn, params=(day, ))
    nc = ncopen(get_daily_ncname(day.year), 'a')
    res = generic_gridder(day, nc, df, 'precip')
    if res is not None:
        offset = daily_offset(day)
        nc.variables['p01d_12z'][offset] = res.to(mpunits('mm')).magnitude
    nc.close()


if __name__ == '__main__':
    main(sys.argv)
