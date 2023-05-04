"""Forecast GFS ~4 inch temperatures, gasp?

Called from gfs2iemre.py for just the 6z run.
"""
# pylint: disable=unbalanced-tuple-unpacking
# stdlib
import datetime

import numpy as np

# thirdparty
import pandas as pd
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import convert_value, get_sqlalchemy_conn, logger, ncopen

LOG = logger()


def get_idx(lons, lats, lon, lat):
    """Return the grid points closest to this point"""
    dist = ((lons - lon) ** 2 + (lats - lat) ** 2) ** 0.5
    return np.unravel_index(dist.argmin(), dist.shape)


def sampler(xaxis, yaxis, vals, x, y):
    """This is a hack"""
    i = 0
    while xaxis[i] < x:
        i += 1
    j = 0
    while yaxis[j] < y:
        j += 1
    return vals[i, j]


def gen_plot(cdf, dt, day, soilt, lons, lats, fx):
    """Make a plot."""
    mp = MapPlot(
        sector="iowa",
        title=(
            "GFS Forecast Average ~4 inch Depth Soil "
            f"Temperatures for {dt:%b %d, %Y}"
        ),
        subtitle=(
            "Caution: Raw output average of 4 (6-hour) forecasts (6z-6z) "
            f"valid for 0-10 cm depth. ({fx})"
        ),
    )
    mp.pcolormesh(
        lons,
        lats,
        soilt,
        np.arange(10, 101, 5),
        cmap=get_cmap("jet"),
        units=r"$^\circ$F",
    )
    mp.plot_values(
        cdf["lon"],
        cdf["lat"],
        cdf["gfs"].values,
        fmt="%.0f",
        textsize=11,
        labelbuffer=5,
    )
    mp.drawcounties()
    pqstr = (
        f"plot c {dt:%Y%m%d}0000 forecast/gfs_soilt_day_f{day}.png "
        f"forecast/gfs_soilt_day_f{day}.png png"
    )
    LOG.info(pqstr)
    mp.postprocess(pqstr=pqstr)
    mp.close()


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("postgis") as conn:
        cdf = pd.read_sql(
            """SELECT ST_x(ST_centroid(the_geom)) as lon,
            ST_y(ST_centroid(the_geom)) as lat
            from uscounties WHERE state_name = 'Iowa'
        """,
            conn,
            index_col=None,
        )
    with ncopen("/mesonet/data/iemre/gfs_current.nc") as nc:
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
        lons, lats = np.meshgrid(lons, lats)
        fx = nc.gfs_forecast
        basedt = datetime.datetime.strptime(
            nc.variables["time"].units.split()[2],
            "%Y-%m-%d",
        )
        for day in range(0, 20):
            dt = basedt + datetime.timedelta(days=day)
            soilk = nc.variables["tsoil"][day, :, :]
            if np.ma.is_masked(np.ma.max(soilk)):
                continue
            soilt = convert_value(soilk, "degK", "degF")
            for i, row in cdf.iterrows():
                x, y = get_idx(lons, lats, row["lon"], row["lat"])
                cdf.at[i, "gfs"] = soilt[x, y]

            gen_plot(cdf, dt, day, soilt, lons, lats, fx)


if __name__ == "__main__":
    main()
