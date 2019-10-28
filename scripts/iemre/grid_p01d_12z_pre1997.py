"""Make a gridded analysis of p01d_12z based on obs."""
import sys
import subprocess
import datetime

import numpy as np
import verde as vd
import pyproj
from metpy.units import units as mpunits
from metpy.units import masked_array
from pandas.io.sql import read_sql
from pyiem.iemre import get_grids, XAXIS, YAXIS
from pyiem.util import get_dbconn


def generic_gridder(day, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    data = df[idx].values
    coordinates = (df["lon"].values, df["lat"].values)
    region = [XAXIS[0], XAXIS[-1], YAXIS[0], YAXIS[-1]]
    projection = pyproj.Proj(proj="merc", lat_ts=df["lat"].mean())
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
    shape = (len(YAXIS), len(XAXIS))
    grid = chain.grid(
        region=region,
        shape=shape,
        projection=projection,
        dims=["latitude", "longitude"],
        data_names=["precip"],
    )
    res = grid.to_array()
    res = np.ma.where(res < 0, 0, res)
    print(
        ("%s %s rows for %s column min:%.3f max:%.3f score: %.3f")
        % (day, len(df.index), idx, np.nanmin(res), np.nanmax(res), score)
    )
    return masked_array(res, mpunits("inch"))


def main(argv):
    """Do work please"""
    day = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    pgconn = get_dbconn("coop")
    df = read_sql(
        """
        SELECT a.precip, st_x(t.geom) as lon, st_y(t.geom) as lat
        from alldata a JOIN stations t ON (a.station = t.id)
        WHERE a.day = %s and t.network ~* 'CLIMATE' and
        substr(a.station,3,4) != '0000' and substr(station,3,1) != 'C'
        and precip >= 0 and precip < 50
    """,
        pgconn,
        params=(day,),
    )
    res = generic_gridder(day, df, "precip")
    if res is not None:
        ds = get_grids(day, varnames="p01d_12z")
        ds["p01d_12z"].values = res.to(mpunits("mm")).magnitude[0, :, :]
        subprocess.call(
            "python db_to_netcdf.py %s" % (day.strftime("%Y %m %d"),),
            shell=True,
        )


if __name__ == "__main__":
    main(sys.argv)
