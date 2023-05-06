"""Make a gridded analysis of p01d_12z based on obs."""
import datetime
import subprocess
import sys

import numpy as np
import pyproj
import verde as vd
from metpy.units import masked_array
from metpy.units import units as mpunits
from pandas import read_sql
from pyiem.iemre import XAXIS, YAXIS, get_grids, set_grids
from pyiem.util import get_dbconnstr, logger

LOG = logger()


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
            ("spline", vd.ScipyGridder(method="nearest")),
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
    LOG.info(
        "%s %s rows for %s column min:%.3f max:%.3f score: %.3f",
        day,
        len(df.index),
        idx,
        np.nanmin(res),
        np.nanmax(res),
        score,
    )
    return masked_array(res, mpunits("inch"))


def main(argv):
    """Do work please"""
    day = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    # Omit any current estimates as these likely have a feedback loop on the
    # IEMRE analysis
    df = read_sql(
        """
        SELECT
        case when a.precip < 0.005 then 0 else a.precip end as precip,
        st_x(t.geom) as lon, st_y(t.geom) as lat
        from alldata a JOIN stations t ON (a.station = t.id)
        WHERE a.day = %s and t.network ~* 'CLIMATE' and
        substr(a.station,3,4) != '0000' and
        substr(station,3,1) not in ('C', 'D', 'T')
        and precip >= 0 and precip < 50
        and not precip_estimated
    """,
        get_dbconnstr("coop"),
        params=(day,),
    )
    res = generic_gridder(day, df, "precip")
    if res is not None:
        ds = get_grids(day, varnames="p01d_12z")
        ds["p01d_12z"].values = res.to(mpunits("mm")).magnitude[0, :, :]
        set_grids(day, ds)
        subprocess.call(
            "python db_to_netcdf.py %s" % (day.strftime("%Y %m %d"),),
            shell=True,
        )


if __name__ == "__main__":
    main(sys.argv)
