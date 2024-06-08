"""
This application attempts to assess the
effectiveness of a calendar day's rainfall based on where the rain fell
in relation to a previous period of days departure from climatology. So
for a given date and state, the areal coverage of daily precipitation
at some given threshold is compared against the departure from climatology
over some given number of days.  The intention is to answer a question like
how much of the rain on a given day fell on an area that needed it!  The
areal coverage percentages are relative to the given state.
"""

import datetime
import os

import geopandas as gpd
import numpy as np
from pyiem import iemre, util
from pyiem.exceptions import NoDataFound
from pyiem.grid.zs import CachingZonalStats
from pyiem.plot import figure_axes
from pyiem.reference import state_names


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="csector", name="sector", default="IA", label="Select Sector:"
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Date:",
            min="2011/01/01",
        ),
        dict(
            type="int",
            name="trailing",
            default=31,
            label="Over how many trailing days to compute departures?",
        ),
        dict(
            type="float",
            name="threshold",
            default=0.1,
            label="Date Precipitation Threshold (inch)",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = util.get_autoplot_context(fdict, get_description())
    date = ctx["date"]
    sector = ctx["sector"]
    days = ctx["trailing"]
    threshold = ctx["threshold"]
    window_sts = date - datetime.timedelta(days=days)
    if window_sts.year != date.year:
        raise NoDataFound("Sorry, do not support multi-year plots yet!")
    if len(sector) != 2:
        raise NoDataFound(
            "Sorry, this does not support multi-state plots yet."
        )

    idx0 = iemre.daily_offset(window_sts)
    idx1 = iemre.daily_offset(date)
    ncfn = iemre.get_daily_mrms_ncname(date.year)
    ncvar = "p01d"
    if not os.path.isfile(ncfn):
        raise NoDataFound("No data for that year, sorry.")
    # Get the state weight
    with util.get_sqlalchemy_conn("postgis") as conn:
        df = gpd.GeoDataFrame.from_postgis(
            "SELECT the_geom from states where state_abbr = %s",
            conn,
            params=(sector,),
            index_col=None,
            geom_col="the_geom",
        )
    czs = CachingZonalStats(iemre.MRMS_AFFINE)
    with util.ncopen(ncfn) as nc:
        czs.gen_stats(
            np.zeros((nc.variables["lat"].size, nc.variables["lon"].size)),
            df["the_geom"],
        )
        hasdata = None
        jslice = None
        islice = None
        for nav in czs.gridnav:
            hasdata = np.ones((nav.ysz, nav.xsz))
            hasdata[nav.mask] = 0.0
            # careful here as y is flipped in this context
            jslice = slice(
                nc.variables["lat"].size - (nav.y0 + nav.ysz),
                nc.variables["lat"].size - nav.y0,
            )
            islice = slice(nav.x0, nav.x0 + nav.xsz)
        hasdata = np.flipud(hasdata)

        today = util.mm2inch(nc.variables[ncvar][idx1, jslice, islice])
        if (idx1 - idx0) < 32:
            p01d = util.mm2inch(
                np.sum(nc.variables[ncvar][idx0:idx1, jslice, islice], 0)
            )
        else:
            # Too much data can overwhelm this app, need to chunk it
            for i in range(idx0, idx1, 10):
                i2 = min([i + 10, idx1])
                if idx0 == i:
                    p01d = util.mm2inch(
                        np.sum(nc.variables[ncvar][i:i2, jslice, islice], 0)
                    )
                else:
                    p01d += util.mm2inch(
                        np.sum(nc.variables[ncvar][i:i2, jslice, islice], 0)
                    )

    # Get climatology
    ncfn = iemre.get_dailyc_mrms_ncname()
    if not os.path.isfile(ncfn):
        raise NoDataFound(f"Missing {ncfn}")
    with util.ncopen(ncfn) as nc:
        if (idx1 - idx0) < 32:
            c_p01d = util.mm2inch(
                np.sum(nc.variables[ncvar][idx0:idx1, jslice, islice], 0)
            )
        else:
            # Too much data can overwhelm this app, need to chunk it
            for i in range(idx0, idx1, 10):
                i2 = min([i + 10, idx1])
                if idx0 == i:
                    c_p01d = util.mm2inch(
                        np.sum(nc.variables[ncvar][i:i2, jslice, islice], 0)
                    )
                else:
                    c_p01d += util.mm2inch(
                        np.sum(nc.variables[ncvar][i:i2, jslice, islice], 0)
                    )

    # we actually don't care about weights at this fine of scale
    cells = np.sum(np.where(hasdata > 0, 1, 0))
    departure = p01d - c_p01d
    # Update departure and today to values unconsidered below when out of state
    departure = np.where(hasdata > 0, departure, -9999)
    today = np.where(hasdata > 0, today, 0)
    ranges = [
        [-99, -3],
        [-3, -2],
        [-2, -1],
        [-1, 0],
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 99],
    ]
    x = []
    x2 = []
    labels = []
    for minv, maxv in ranges:
        labels.append(f"{minv:.0f} to {maxv:.0f}")
        # How many departure cells in this range
        hits = np.logical_and(departure < maxv, departure > minv)
        hits2 = np.logical_and(hits, today > threshold)
        x.append(np.sum(np.where(hits, 1, 0)) / float(cells) * 100.0)
        x2.append(np.sum(np.where(hits2, 1, 0)) / float(cells) * 100.0)

    title = (
        f"{state_names[sector]} NOAA MRMS {date:%-d %b %Y} "
        f"{threshold:.2f} inch Precip Coverage"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.bar(
        np.arange(8) - 0.2,
        x,
        align="center",
        width=0.4,
        label=f"Trailing {days} Day Departure",
    )
    ax.bar(
        np.arange(8) + 0.2,
        x2,
        align="center",
        width=0.4,
        label=f"{date:%-d %b %Y} Coverage ({sum(x2):.1f}% Tot)",
    )
    for i, (_x1, _x2) in enumerate(zip(x, x2)):
        ax.text(i - 0.2, _x1 + 1, f"{_x1:.1f}", ha="center")
        ax.text(i + 0.2, _x2 + 1, f"{_x2:.1f}", ha="center")
    ax.set_xticks(np.arange(8))
    ax.set_xticklabels(labels)
    ax.set_xlabel(f"Trailing {days} Day Precip Departure [in]")
    ax.set_position([0.1, 0.2, 0.8, 0.7])
    ax.legend(loc=(0.0, -0.2), ncol=2)
    ax.set_ylabel(f"Areal Coverage of {state_names[sector]} [%]")
    ax.grid(True)
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(0, max([max(x2), max(x)]) + 5)
    return fig


if __name__ == "__main__":
    plotter({})
