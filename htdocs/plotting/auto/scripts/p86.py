"""Plot IEMRE"""
import datetime
import os

import numpy as np
from pyiem import iemre
from pyiem.plot import MapPlot
from pyiem.plot.colormaps import stretch_cmap
from pyiem.util import get_autoplot_context, ncopen
from pyiem.exceptions import NoDataFound
from pyiem.reference import LATLON
from metpy.units import units, masked_array

PDICT = dict(
    (
        ("p01d_12z", "24 Hour Precipitation at 12 UTC"),
        ("p01d", "Calendar Day Precipitation"),
        ("range_tmpk", "Range between Min and Max Temp"),
        ("range_tmpk_12z", "Range between Min and Max Temp at 12 UTC"),
        ("low_tmpk", "Minimum Temperature"),
        ("low_tmpk_12z", "Minimum Temperature at 12 UTC"),
        ("high_tmpk", "Maximum Temperature"),
        ("high_tmpk_12z", "Maximum Temperature at 12 UTC"),
        ("p01d", "Calendar Day Precipitation"),
        ("power_swdn", "NASA POWER :: Incident Shortwave Down"),
        ("rsds", "Solar Radiation"),
        ("avg_dwpk", "Average Dew Point"),
        ("wind_speed", "Average Wind Speed"),
        ("snow_12z", "Experimental 24-Hour Snowfall at 12 UTC"),
        ("snowd_12z", "Experimental 24-Hour Snow Depth at 12 UTC"),
    )
)
PDICT2 = {"c": "Contour Plot", "g": "Grid Cell Mesh"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc[
        "description"
    ] = """This map presents a daily IEM ReAnalysis variable
    of your choice.
    """
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="csector",
            name="csector",
            default="midwest",
            label="Select state/sector to plot",
        ),
        dict(
            type="select",
            name="var",
            default="rsds",
            label="Select Plot Variable:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="ptype",
            default="c",
            label="Select Plot Type:",
            options=PDICT2,
        ),
        dict(
            type="date",
            name="date",
            default=today.strftime("%Y/%m/%d"),
            label="Date:",
            min="1893/01/01",
        ),
        dict(type="cmap", name="cmap", default="magma", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ptype = ctx["ptype"]
    date = ctx["date"]
    varname = ctx["var"]
    csector = ctx["csector"]
    title = date.strftime("%-d %B %Y")
    mp = MapPlot(
        sector=("state" if len(csector) == 2 else csector),
        state=ctx["csector"],
        axisbg="white",
        nocaption=True,
        title=f"IEM Reanalysis of {PDICT.get(varname)} for {title}",
        subtitle="Data derived from various NOAA datasets",
    )
    (west, east, south, north) = mp.ax.get_extent(LATLON)
    i0, j0 = iemre.find_ij(west, south)
    i1, j1 = iemre.find_ij(east, north)
    jslice = slice(j0, j1)
    islice = slice(i0, i1)

    idx0 = iemre.daily_offset(date)
    ncfn = iemre.get_daily_ncname(date.year)
    if not os.path.isfile(ncfn):
        raise NoDataFound("No Data Found.")
    with ncopen(ncfn) as nc:
        lats = nc.variables["lat"][jslice]
        lons = nc.variables["lon"][islice]
        cmap = ctx["cmap"]
        if varname in ["rsds", "power_swdn"]:
            # Value is in W m**-2, we want MJ
            multi = (86400.0 / 1000000.0) if varname == "rsds" else 1
            data = nc.variables[varname][idx0, jslice, islice] * multi
            plot_units = "MJ d-1"
            clevs = np.arange(0, 37, 3.0)
            clevs[0] = 0.01
            clevstride = 1
        elif varname in ["wind_speed"]:
            data = (
                masked_array(
                    nc.variables[varname][idx0, jslice, islice],
                    units("meter / second"),
                )
                .to(units("mile / hour"))
                .m
            )
            plot_units = "mph"
            clevs = np.arange(0, 41, 2)
            clevs[0] = 0.01
            clevstride = 2
        elif varname in ["p01d", "p01d_12z", "snow_12z", "snowd_12z"]:
            # Value is in W m**-2, we want MJ
            data = (
                masked_array(
                    nc.variables[varname][idx0, jslice, islice], units("mm")
                )
                .to(units("inch"))
                .m
            )
            plot_units = "inch"
            clevs = np.arange(0, 0.25, 0.05)
            clevs = np.append(clevs, np.arange(0.25, 3.0, 0.25))
            clevs = np.append(clevs, np.arange(3.0, 10.0, 1))
            clevs[0] = 0.01
            clevstride = 1
            cmap = stretch_cmap(ctx["cmap"], clevs)
        elif varname in [
            "high_tmpk",
            "low_tmpk",
            "high_tmpk_12z",
            "low_tmpk_12z",
            "avg_dwpk",
        ]:
            # Value is in W m**-2, we want MJ
            data = (
                masked_array(
                    nc.variables[varname][idx0, jslice, islice], units("degK")
                )
                .to(units("degF"))
                .m
            )
            plot_units = "F"
            clevs = np.arange(-30, 120, 5)
            clevstride = 2
        elif varname in ["range_tmpk", "range_tmpk_12z"]:
            vname1 = "high_tmpk%s" % (
                "_12z" if varname == "range_tmpk_12z" else "",
            )
            vname2 = "low_tmpk%s" % (
                "_12z" if varname == "range_tmpk_12z" else "",
            )
            d1 = nc.variables[vname1][idx0, jslice, islice]
            d2 = nc.variables[vname2][idx0, jslice, islice]
            data = (
                masked_array(d1, units("degK")).to(units("degF")).m
                - masked_array(d2, units("degK")).to(units("degF")).m
            )
            plot_units = "F"
            clevs = np.arange(0, 61, 5)
            clevstride = 2

    if np.ma.is_masked(np.max(data)):
        raise NoDataFound("Data Unavailable")
    x, y = np.meshgrid(lons, lats)
    if ptype == "c":
        # in the case of contour, use the centroids on the grids
        mp.contourf(
            x + 0.125,
            y + 0.125,
            data,
            clevs,
            clevstride=clevstride,
            units=plot_units,
            ilabel=True,
            labelfmt="%.0f",
            cmap=cmap,
        )
    else:
        x, y = np.meshgrid(lons, lats)
        mp.pcolormesh(
            x,
            y,
            data,
            clevs,
            clevstride=clevstride,
            cmap=cmap,
            units=plot_units,
        )

    return mp.fig


if __name__ == "__main__":
    plotter(dict(ptype="g", date="2016-01-03", var="high_tmpk_12z"))
