"""Precip estimates"""
from datetime import datetime, timedelta
import os
from collections import OrderedDict

import numpy as np
from pyiem import iemre, util
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import state_bounds, SECTORS
from pyiem.exceptions import NoDataFound
from metpy.units import units, masked_array

PDICT2 = {"c": "Contour Plot", "g": "Grid Cell Mesh"}
SRCDICT = OrderedDict(
    (
        ("iemre", "IEM Reanalysis (since 1 Jan 1893)"),
        ("mrms", "NOAA MRMS (since 1 Jan 2014)"),
        ("prism", "OSU PRISM (since 1 Jan 1981)"),
    )
)
PDICT3 = {
    "acc": "Accumulation",
    "dep": "Departure from Average [inch]",
    "per": "Percent of Average [%]",
}
PDICT4 = {
    "yes": "Yes, overlay Drought Monitor",
    "no": "No, do not overlay Drought Monitor",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = False
    desc[
        "description"
    ] = """This application generates maps of precipitation
    daily or multi-day totals.  There are currently three backend data sources
    made available to this plotting application:
    <ul>
      <li><a href="/iemre/">IEM Reanalysis</a>
      <br />A crude gridding of available COOP data and long term climate data
      processed by the IEM. The plotted totals represent periods typical to
      COOP data reporting, which is roughly 12 UTC (7 AM local) each day.</li>
      <li><a href="https://www.nssl.noaa.gov/projects/mrms/">NOAA MRMS</a>
      <br />A state of the art gridded analysis of RADAR data using
      observations and model data to help in the processing.</li>
      <li><a href="http://prism.oregonstate.edu">Oregon State PRISM</a>
      <br />The PRISM data is credit Oregon State University,
      created 4 Feb 2004.  This information arrives with a few day lag. The
      plotted totals represent periods typical to COOP data reporting, so
      12 UTC (7 AM local) each day.</li>
    </ul>
    """
    today = datetime.today() - timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="csector", name="sector", default="IA", label="Select Sector:"
        ),
        dict(
            type="select",
            name="src",
            default="mrms",
            label="Select Source:",
            options=SRCDICT,
        ),
        dict(
            type="select",
            name="opt",
            default="acc",
            label="Plot Precipitation As:",
            options=PDICT3,
        ),
        dict(
            type="select",
            name="usdm",
            default="no",
            label="Overlay Drought Monitor",
            options=PDICT4,
        ),
        dict(
            type="select",
            name="ptype",
            default="g",
            label="Select Plot Type:",
            options=PDICT2,
        ),
        dict(
            type="date",
            name="sdate",
            default=today.strftime("%Y/%m/%d"),
            label="Start Date:",
            min="1893/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date:",
            min="1893/01/01",
        ),
        dict(type="cmap", name="cmap", default="YlGnBu", label="Color Ramp:"),
    ]
    return desc


def mm2inch(val):
    """Helper."""
    return masked_array(val, units("mm")).to(units("inch")).m


def compute_title(src, sdate, edate):
    """Figure out how to label this fun."""
    title = "Fixme"
    if src == "mrms":
        # This is generally closer to 'daily
        if sdate == edate:
            title = sdate.strftime("%-d %B %Y")
        else:
            title = "%s to %s (inclusive)" % (
                sdate.strftime("%-d %b"),
                edate.strftime("%-d %b %Y"),
            )
    else:
        # This is 12z to 12z totals.
        if sdate == edate:
            title = "%s ~12z to %s ~12z" % (
                (sdate - timedelta(days=1)).strftime("%-d %B %Y"),
                edate.strftime("%-d %B %Y"),
            )
        else:
            title = "%s ~12z to %s ~12z" % (
                (sdate - timedelta(days=1)).strftime("%-d %B %Y"),
                (edate + timedelta(days=1)).strftime("%-d %B %Y"),
            )
    return title


def plotter(fdict):
    """ Go """
    ctx = util.get_autoplot_context(fdict, get_description())
    ptype = ctx["ptype"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    src = ctx["src"]
    opt = ctx["opt"]
    usdm = ctx["usdm"]
    if sdate.year != edate.year:
        raise NoDataFound("Sorry, do not support multi-year plots yet!")
    days = (edate - sdate).days
    sector = ctx["sector"]

    x0 = 0
    x1 = -1
    y0 = 0
    y1 = -1
    state = None
    if len(sector) == 2:
        state = sector
        sector = "state"

    title = compute_title(src, sdate, edate)
    if src == "mrms":
        ncfn = iemre.get_daily_mrms_ncname(sdate.year)
        clncfn = iemre.get_dailyc_mrms_ncname()
        ncvar = "p01d"
        source = "MRMS Q3"
        subtitle = "NOAA MRMS Project, GaugeCorr and RadarOnly"
    elif src == "iemre":
        ncfn = iemre.get_daily_ncname(sdate.year)
        clncfn = iemre.get_dailyc_ncname()
        ncvar = "p01d_12z"
        source = "IEM Reanalysis"
        subtitle = "IEM Reanalysis is derived from various NOAA datasets"
    else:
        ncfn = "/mesonet/data/prism/%s_daily.nc" % (sdate.year,)
        clncfn = "/mesonet/data/prism/prism_dailyc.nc"
        ncvar = "ppt"
        source = "OSU PRISM"
        subtitle = (
            "PRISM Climate Group, Oregon State Univ., "
            "http://prism.oregonstate.edu, created 4 Feb 2004."
        )

    mp = MapPlot(
        sector=sector,
        state=state,
        axisbg="white",
        nocaption=True,
        title="%s:: %s Precip %s" % (source, title, PDICT3[opt]),
        subtitle="Data from %s" % (subtitle,),
        titlefontsize=14,
    )

    idx0 = iemre.daily_offset(sdate)
    idx1 = iemre.daily_offset(edate) + 1
    if not os.path.isfile(ncfn):
        raise NoDataFound("No data for that year, sorry.")
    with util.ncopen(ncfn) as nc:
        if state is not None:
            x0, y0, x1, y1 = util.grid_bounds(
                nc.variables["lon"][:],
                nc.variables["lat"][:],
                state_bounds[state],
            )
        elif sector in SECTORS:
            bnds = SECTORS[sector]
            x0, y0, x1, y1 = util.grid_bounds(
                nc.variables["lon"][:],
                nc.variables["lat"][:],
                [bnds[0], bnds[2], bnds[1], bnds[3]],
            )
        lats = nc.variables["lat"][y0:y1]
        lons = nc.variables["lon"][x0:x1]
        if sdate == edate:
            p01d = mm2inch(nc.variables[ncvar][idx0, y0:y1, x0:x1])
        elif (idx1 - idx0) < 32:
            p01d = mm2inch(
                np.sum(nc.variables[ncvar][idx0:idx1, y0:y1, x0:x1], 0)
            )
        else:
            # Too much data can overwhelm this app, need to chunk it
            for i in range(idx0, idx1, 10):
                i2 = min([i + 10, idx1])
                if idx0 == i:
                    p01d = mm2inch(
                        np.sum(nc.variables[ncvar][i:i2, y0:y1, x0:x1], 0)
                    )
                else:
                    p01d += mm2inch(
                        np.sum(nc.variables[ncvar][i:i2, y0:y1, x0:x1], 0)
                    )
    if np.ma.is_masked(np.max(p01d)):
        raise NoDataFound("Data Unavailable")
    plot_units = "inches"
    cmap = get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    if opt == "dep":
        # Do departure work now
        with util.ncopen(clncfn) as nc:
            climo = mm2inch(
                np.sum(nc.variables[ncvar][idx0:idx1, y0:y1, x0:x1], 0)
            )
        p01d = p01d - climo
        [maxv] = np.percentile(np.abs(p01d), [99])
        clevs = np.around(np.linspace(0 - maxv, maxv, 11), decimals=2)
    elif opt == "per":
        with util.ncopen(clncfn) as nc:
            climo = mm2inch(
                np.sum(nc.variables[ncvar][idx0:idx1, y0:y1, x0:x1], 0)
            )
        p01d = p01d / climo * 100.0
        cmap.set_under("white")
        cmap.set_over("black")
        clevs = [1, 10, 25, 50, 75, 100, 125, 150, 200, 300, 500]
        plot_units = "percent"
    else:
        p01d = np.where(p01d < 0.001, np.nan, p01d)
        cmap.set_under("white")
        clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
        if days > 6:
            clevs = [0.01, 0.3, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20]
        if days > 29:
            clevs = [0.01, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 35]
        if days > 90:
            clevs = [0.01, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30, 35, 40]

    x2d, y2d = np.meshgrid(lons, lats)
    if ptype == "c":
        mp.contourf(
            x2d, y2d, p01d, clevs, cmap=cmap, units=plot_units, iline=False
        )
    else:
        res = mp.pcolormesh(x2d, y2d, p01d, clevs, cmap=cmap, units=plot_units)
        res.set_rasterized(True)
    if sector != "midwest":
        mp.drawcounties()
        mp.drawcities()
    if usdm == "yes":
        mp.draw_usdm(edate, filled=False, hatched=True)

    return mp.fig


if __name__ == "__main__":
    plotter(dict())
