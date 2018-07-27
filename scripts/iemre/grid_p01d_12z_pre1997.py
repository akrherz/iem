"""Make a gridded analysis of p01d_12z based on obs."""
import sys
import datetime

import numpy as np
from metpy.units import units as mpunits
from scipy.interpolate import NearestNDInterpolator
from pandas.io.sql import read_sql
from pyiem.iemre import get_daily_ncname, daily_offset
from pyiem.util import ncopen, get_dbconn


def generic_gridder(day, nc, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    xi, yi = np.meshgrid(nc.variables['lon'][:], nc.variables['lat'][:])
    nn = NearestNDInterpolator((df['lon'].values,
                                df['lat'].values),
                               df[idx].values)
    grid = nn(xi, yi)
    print(("%s %s rows for %s column min:%.3f max:%.3f"
           ) % (day, len(df.index), idx, np.min(grid), np.max(grid)))
    if grid is not None:
        return grid
    return None


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
        nc.variables['p01d_12z'][offset] = (
            res * mpunits['inch']).to(mpunits['mm']).magnitude
    nc.close()


if __name__ == '__main__':
    main(sys.argv)
