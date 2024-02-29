"""
Generate a number of plots showing:
 1) Last 4 month's precipitation
 2) Normal for past 4 months
 3) Departure for this period

 We care about 4 months as it is used in drought analysis
"""

import datetime

import numpy as np
from pyiem import iemre
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import ncopen


def main():
    """Go Main Go"""
    # Run for a period of 121 days
    ets = datetime.datetime.now() - datetime.timedelta(days=1)
    sts = ets - datetime.timedelta(days=121)

    # Get the normal accumm
    with ncopen(iemre.get_dailyc_ncname(), "r") as cnc:
        lons = cnc.variables["lon"][:]
        lats = cnc.variables["lat"][:]
        index0 = iemre.daily_offset(sts)
        index1 = iemre.daily_offset(ets)
        if index1 < index0:  # Uh oh, we are spanning a year
            clprecip = np.sum(cnc.variables["p01d"][:index1, :, :], 0)
            clprecip = clprecip + np.sum(
                cnc.variables["p01d"][index0:, :, :], 0
            )
        else:
            clprecip = np.sum(cnc.variables["p01d"][index0:index1, :, :], 0)

    # Get the observed precip
    if sts.year != ets.year:  # spanner, darn
        with ncopen(iemre.get_daily_ncname(sts.year)) as onc:
            obprecip = np.sum(onc.variables["p01d"][index0:, :, :], 0)
        with ncopen(iemre.get_daily_ncname(ets.year)) as onc:
            obprecip = obprecip + np.sum(
                onc.variables["p01d"][:index1, :, :], 0
            )
    else:
        ncfn = iemre.get_daily_ncname(sts.year)
        with ncopen(ncfn, "r") as onc:
            obprecip = np.sum(onc.variables["p01d"][index0:index1, :, :], 0)

    lons, lats = np.meshgrid(lons, lats)

    # Plot departure from normal
    mp = MapPlot(
        sector="midwest",
        title=f"Precipitation Departure {sts:%b %d %Y} - {ets:%b %d %Y}",
        subtitle="based on IEM Estimates",
    )

    mp.pcolormesh(
        lons,
        lats,
        (obprecip - clprecip) / 25.4,
        np.arange(-10, 10, 1),
        cmap=get_cmap("RdBu"),
    )
    mp.postprocess(pqstr="plot c 000000000000 summary/4mon_diff.png bogus png")
    mp.close()

    # Plot normals
    mp = MapPlot(
        sector="midwest",
        title=f"Normal Precipitation:: {sts:%b %d %Y} - {ets:%b %d %Y}",
        subtitle="based on IEM Estimates",
    )

    mp.pcolormesh(lons, lats, (clprecip) / 25.4, np.arange(0, 30, 2))
    mp.postprocess(
        pqstr="plot c 000000000000 summary/4mon_normals.png bogus png"
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
        pqstr="plot c 000000000000 summary/4mon_stage4obs.png bogus png"
    )
    mp.close()


if __name__ == "__main__":
    main()
