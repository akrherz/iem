"""
This map presents a daily <a href="/iemre/">IEM ReAnalysis</a> variable
of your choice.  The concept of a day within this dataset is a period
between 6 UTC to 6 UTC, which is Central Standard Time all year round.</p>

<p><a href="/plotting/auto/?q=249">Autoplot 249</a> is the hourly
variant of this plot.
"""

import os
from datetime import datetime, timedelta

import numpy as np
from metpy.units import masked_array, units
from pyiem.exceptions import NoDataFound
from pyiem.grid.nav import get_nav
from pyiem.iemre import daily_offset, get_daily_ncname
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import ncopen

from iemweb.autoplot import ARG_IEMRE_DOMAIN

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
PDICT3 = {
    "yes": "Mask Data Outside Plot Geography",
    "no": "Do Not Mask Data Outside Plot Geography",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    today = datetime.today() - timedelta(days=1)
    desc["arguments"] = [
        ARG_IEMRE_DOMAIN,
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
        {
            "type": "select",
            "name": "clip",
            "default": "yes",
            "label": "Clip Data Outside Plot Geography:",
            "options": PDICT3,
        },
        dict(type="cmap", name="cmap", default="magma", label="Color Ramp:"),
    ]
    return desc


def unit_convert(nc, varname, idx0):
    """Convert units."""
    data = None
    if not varname.startswith("range"):
        data = nc.variables[varname][idx0]
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
        d1 = nc.variables[vname1][idx0]
        d2 = nc.variables[vname2][idx0]
        data = (
            masked_array(d1, units("degK")).to(units("degF")).m
            - masked_array(d2, units("degK")).to(units("degF")).m
        )
    return data


def plotter(ctx: dict):
    """Go"""
    domain = ctx["domain"]
    gridnav = get_nav("iemre", domain)
    ptype = ctx["ptype"]
    dt = ctx["date"]
    varname = ctx["var"]
    mpargs = {
        "title": f"IEM Reanalysis of {PDICT.get(varname)} for {dt:%-d %b %Y}",
        "subtitle": "Data derived from various NOAA datasets",
        "axisbg": "white",
        "nocaption": True,
        "apctx": ctx,
    }
    if domain != "":
        ctx["csector"] = "custom"
        mpargs["west"] = gridnav.left_edge
        mpargs["east"] = gridnav.right_edge
        mpargs["south"] = gridnav.bottom_edge
        mpargs["north"] = gridnav.top_edge

    mp = MapPlot(**mpargs)

    plot_units = ""
    idx0 = daily_offset(dt)
    ncfn = get_daily_ncname(dt.year, domain=domain)
    if not os.path.isfile(ncfn):
        raise NoDataFound("No Data Found.")
    with ncopen(ncfn) as nc:
        cmap = get_cmap(ctx["cmap"])
        data = unit_convert(nc, varname, idx0)
        if np.ma.is_masked(data) and data.mask.all():
            raise NoDataFound("All data is missing.")
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

    if ptype == "c":
        x, y = np.meshgrid(gridnav.x_points, gridnav.y_points)
        mp.contourf(
            x,
            y,
            data,
            clevs,
            units=plot_units,
            ilabel=True,
            labelfmt="%.0f",
            cmap=cmap,
            clip_on=ctx["clip"] == "yes",
        )
    else:
        mp.imshow(
            data,
            gridnav.affine,
            gridnav.crs,
            clevs=clevs,
            cmap=cmap,
            units=plot_units,
            clip_on=ctx["clip"] == "yes",
        )

    return mp.fig
