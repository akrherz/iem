"""Make a gridded analysis of p01d_12z based on obs."""
import sys
import datetime

import numpy as np
import verde as vd
import pyproj
from metpy.units import units as mpunits
from metpy.units import masked_array
from pandas.io.sql import read_sql
from pyiem.iemre import get_daily_ncname, daily_offset
from pyiem.util import ncopen, get_dbconn


def generic_gridder(day, nc, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    data = df[idx].values
    coordinates = (df['lon'].values, df['lat'].values)
    region = [
        nc.variables['lon'][0],
        nc.variables['lon'][-1],
        nc.variables['lat'][0],
        nc.variables['lat'][-1],
    ]
    projection = pyproj.Proj(proj="merc", lat_ts=df['lat'].mean())
    spacing = 0.5
    chain = vd.Chain(
        [
            ("mean", vd.BlockReduce(np.mean, spacing=spacing * 111e3)),
            ("spline", vd.Spline(damping=1e-10, mindist=100e3)),
        ]
    )
    train, test = vd.train_test_split(
        projection(*coordinates), data, random_state=0
    )
    chain.fit(*train)
    score = chain.score(*test)
    shape = (nc.dimensions['lat'].size, nc.dimensions['lon'].size)
    grid = chain.grid(
        region=region,
        shape=shape,
        projection=projection,
        dims=["latitude", "longitude"],
        data_names=["precip"],
    )
    res = grid.to_array()
    res = np.ma.where(res < 0, 0, res)
    print(("%s %s rows for %s column min:%.3f max:%.3f score: %.3f"
           ) % (day, len(df.index), idx, np.nanmin(res),
                np.nanmax(res), score))
    return masked_array(res, mpunits('inch'))


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
