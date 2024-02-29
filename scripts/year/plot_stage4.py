"""Some stage IV plots.

Run from RUN_SUMMARY.sh
"""

import datetime

import numpy as np
from pyiem import iemre
from pyiem.plot import MapPlot
from pyiem.util import ncopen


def main():
    """Go Main Go"""
    ets = datetime.datetime.now() - datetime.timedelta(days=1)
    sts = datetime.datetime(ets.year, 1, 1)

    # Get the normal accumm
    with ncopen(iemre.get_dailyc_ncname()) as cnc:
        lons = cnc.variables["lon"][:]
        lats = cnc.variables["lat"][:]
        index0 = iemre.daily_offset(sts)
        index1 = iemre.daily_offset(ets)
        clprecip = np.sum(cnc.variables["p01d"][index0:index1, :, :], 0)

    with ncopen(iemre.get_daily_ncname(sts.year)) as nc:
        obprecip = np.sum(nc.variables["p01d"][index0:index1, :, :], 0)

    lons, lats = np.meshgrid(lons, lats)

    # Plot departure from normal
    mp = MapPlot(
        sector="midwest",
        title=f"Precipitation Departure {sts:%b %d %Y} - {ets:%b %d %Y}",
        subtitle="based on IEM Estimates",
    )

    mp.pcolormesh(
        lons, lats, (obprecip - clprecip) / 25.4, np.arange(-10, 10, 1)
    )
    mp.postprocess(
        pqstr="plot c 000000000000 summary/year/stage4_diff.png bogus png"
    )
    mp.close()

    # Plot normals
    mp = MapPlot(
        sector="midwest",
        title=f"Normal Precipitation:: {sts:%b %d %Y} - {ets:%b %d %Y}",
        subtitle="based on IEM Estimates",
    )

    mp.pcolormesh(lons, lats, (clprecip) / 25.4, np.arange(0, 30, 2))
    mp.postprocess(
        pqstr="plot c 000000000000 summary/year/stage4_normals.png bogus png"
    )
    mp.close()

    # Plot Obs
    mp = MapPlot(
        sector="midwest",
        title=f"Estimated Precipitation:: {sts:%b %d %Y} - {ets:%b %d %Y}",
        subtitle="based on IEM Estimates",
    )

    mp.pcolormesh(lons, lats, (obprecip) / 25.4, np.arange(0, 30, 2))
    mp.postprocess(
        pqstr="plot c 000000000000 summary/year/stage4obs.png bogus png"
    )
    mp.close()


if __name__ == "__main__":
    main()
