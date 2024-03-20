"""
This map presents a daily <a href="/iemre/">IEM ReAnalysis</a> variable
of your choice.  The concept of a day within this dataset is a period
between 6 UTC to 6 UTC, which is Central Standard Time all year round.</p>

<p><a href="/plotting/auto/?q=249">Autoplot 249</a> is the hourly
variant of this plot.
"""

import datetime
import os

import numpy as np
from metpy.units import masked_array, units
from pyiem import iemre
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.reference import LATLON
from pyiem.util import get_autoplot_context, ncopen

PDICT = {
    "p01d_12z": "24 Hour Precipitation at 12 UTC",
    "p01d": "Calendar Day Precipitation",
    "range_tmpk": "Range between Min and Max Temp",
    "range_tmpk_12z": "Range between Min and Max Temp at 12 UTC",
    "low_tmpk": "Minimum Temperature",
    "low_tmpk_12z": "Minimum Temperature at 12 UTC",
    "high_tmpk": "Maximum Temperature",
    "high_tmpk_12z": "Maximum Temperature at 12 UTC",
    "high_soil4t": "Maximum 4 Inch Soil Temperature",
    "low_soil4t": "Minimum 4 Inch Soil Temperature",
    "min_rh": "Minimum Relative Humidity",
    "max_rh": "Maximum Relative Humidity",
    "power_swdn": "NASA POWER :: Incident Shortwave Down",
    "rsds": "Solar Radiation",
    "avg_dwpk": "Average Dew Point",
    "wind_speed": "Average Wind Speed",
    "snow_12z": "Experimental 24-Hour Snowfall at 12 UTC",
    "snowd_12z": "Experimental 24-Hour Snow Depth at 12 UTC",
}
PDICT2 = {"c": "Contour Plot", "g": "Grid Cell Mesh"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
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


def unit_convert(nc, varname, idx0, jslice, islice):
    """Convert units."""
    data = None
    if not varname.startswith("range"):
        data = nc.variables[varname][idx0, jslice, islice]
    if varname in ["min_rh", "max_rh"]:
        pass
    elif varname in ["rsds", "power_swdn"]:
        # Value is in W m**-2, we want MJ
        multi = (86400.0 / 1000000.0) if varname == "rsds" else 1
        data = data * multi
    elif varname in ["wind_speed"]:
        data = (
            masked_array(
                data,
                units("meter / second"),
            )
            .to(units("mile / hour"))
            .m
        )
    elif varname in ["p01d", "p01d_12z", "snow_12z", "snowd_12z"]:
        # Value is in W m**-2, we want MJ
        data = masked_array(data, units("mm")).to(units("inch")).m
    elif varname in [
        "high_tmpk",
        "low_tmpk",
        "high_tmpk_12z",
        "low_tmpk_12z",
        "avg_dwpk",
        "high_soil4t",
        "low_soil4t",
    ]:
        data = masked_array(data, units("degK")).to(units("degF")).m
    else:  # range_tmpk range_tmpk_12z
        vname2 = f"low_tmpk{'_12z' if varname == 'range_tmpk_12z' else ''}"
        vname1 = vname2.replace("low", "high")
        d1 = nc.variables[vname1][idx0, jslice, islice]
        d2 = nc.variables[vname2][idx0, jslice, islice]
        data = (
            masked_array(d1, units("degK")).to(units("degF")).m
            - masked_array(d2, units("degK")).to(units("degF")).m
        )
    return data


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ptype = ctx["ptype"]
    date = ctx["date"]
    varname = ctx["var"]
    title = date.strftime("%-d %B %Y")
    mp = MapPlot(
        apctx=ctx,
        axisbg="white",
        nocaption=True,
        title=f"IEM Reanalysis of {PDICT.get(varname)} for {title}",
        subtitle="Data derived from various NOAA datasets",
    )
    (west, east, south, north) = mp.panels[0].get_extent(LATLON)
    i0, j0 = iemre.find_ij(west, south)
    i1, j1 = iemre.find_ij(east, north)
    jslice = slice(j0, j1)
    islice = slice(i0, i1)

    plot_units = ""
    idx0 = iemre.daily_offset(date)
    ncfn = iemre.get_daily_ncname(date.year)
    if not os.path.isfile(ncfn):
        raise NoDataFound("No Data Found.")
    with ncopen(ncfn) as nc:
        lats = nc.variables["lat"][jslice]
        lons = nc.variables["lon"][islice]
        cmap = get_cmap(ctx["cmap"])
        data = unit_convert(nc, varname, idx0, jslice, islice)
        if np.ma.is_masked(np.max(data)):
            raise NoDataFound("Data Unavailable")
        ptiles = np.nanpercentile(data.filled(np.nan), [5, 95, 99.9])
        if varname in ["rsds", "power_swdn"]:
            plot_units = "MJ d-1"
            clevs = pretty_bins(0, ptiles[1])
            clevs[0] = 0.01
            cmap.set_under("white")
        elif varname in ["wind_speed"]:
            plot_units = "mph"
            clevs = pretty_bins(0, ptiles[1])
            clevs[0] = 0.01
        elif varname in ["min_rh", "max_rh"]:
            plot_units = "%"
            clevs = pretty_bins(0, 100)
        elif varname in ["p01d", "p01d_12z", "snow_12z", "snowd_12z"]:
            plot_units = "inch"
            if ptiles[2] < 1:
                clevs = np.arange(0, 1.01, 0.1)
            else:
                clevs = pretty_bins(0, ptiles[2])
            clevs[0] = 0.01
            cmap.set_under("white")
        elif varname in [
            "high_tmpk",
            "low_tmpk",
            "high_tmpk_12z",
            "low_tmpk_12z",
            "avg_dwpk",
            "high_soil4t",
            "low_soil4t",
            "range_tmpk",
            "range_tmpk_12z",
        ]:
            plot_units = "F"
            clevs = pretty_bins(ptiles[0], ptiles[1])

    x, y = np.meshgrid(lons, lats)
    if ptype == "c":
        # in the case of contour, use the centroids on the grids
        mp.contourf(
            x + 0.125,
            y + 0.125,
            data,
            clevs,
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
            cmap=cmap,
            units=plot_units,
        )

    return mp.fig


if __name__ == "__main__":
    plotter({})
