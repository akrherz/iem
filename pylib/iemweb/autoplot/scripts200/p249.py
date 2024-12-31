"""
This map presents an hourly <a href="/iemre/">IEM ReAnalysis</a> variable
of your choice. <a href="/plotting/auto/?q=86">Autoplot 86</a> is the daily
variant of this plot.
"""

import os
from datetime import datetime, timedelta, timezone

import numpy as np
from metpy.units import masked_array, units
from pyiem.exceptions import NoDataFound
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_hourly_ncname, hourly_offset
from pyiem.plot import MapPlot, get_cmap, pretty_bins
from pyiem.util import ncopen

from iemweb.autoplot import ARG_IEMRE_DOMAIN

PDICT = {
    "tmpk": "2m Air Temperature",
    "dwpk": "2m Dew Point Temperature",
    "skyc": "Sky Coverage",
    "wind_speed": "10m Wind Speed",
    "p01m": "1 Hour Precipitation",
    "soil4t": "~0-10cm Soil Temperature",
    "rsds": "Hourly Solar Radiation",
}
PDICT2 = {"c": "Contour Plot", "g": "Grid Cell Mesh"}
PDICT3 = {
    "yes": "Yes, mask the plot when appropriate",
    "no": "No, do not mask the plot",
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
            default="tmpk",
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
            type="datetime",
            name="valid",
            default=today.strftime("%Y/%m/%d 0000"),
            label="UTC Timestamp:",
            min="1950/01/01 0000",
        ),
        {
            "type": "select",
            "name": "clip",
            "default": "yes",
            "label": "Mask Plot Data?",
            "options": PDICT3,
        },
        dict(type="cmap", name="cmap", default="magma", label="Color Ramp:"),
    ]
    return desc


def unit_convert(nc, varname, idx0):
    """Convert units."""
    if varname == "wind_speed":
        data = (
            nc.variables["uwnd"][idx0] ** 2 + nc.variables["vwnd"][idx0] ** 2
        ) ** 0.5
        data = (
            masked_array(
                data,
                units("meter / second"),
            )
            .to(units("mile / hour"))
            .m
        )
    else:
        data = nc.variables[varname][idx0]
    if varname in [
        "p01m",
    ]:
        data = masked_array(data, units("mm")).to(units("inch")).m
    elif varname in [
        "tmpk",
        "dwpk",
        "soil4t",
    ]:
        data = masked_array(data, units("degK")).to(units("degF")).m
    return data


def plotter(ctx: dict):
    """Go"""
    domain = ctx["domain"]
    gridnav = get_nav("iemre", domain)
    ptype = ctx["ptype"]
    valid = ctx["valid"].replace(tzinfo=timezone.utc)
    varname = ctx["var"]
    title = valid.strftime("%-d %B %Y %H:%M UTC")
    mpargs = {
        "apctx": ctx,
        "axisbg": "white",
        "nocaption": True,
        "title": f"IEM Reanalysis of {PDICT.get(varname)} for {title}",
        "subtitle": "Data derived from various NOAA/ERA5-Land datasets",
    }
    if domain != "":
        ctx["csector"] = "custom"
        mpargs["east"] = gridnav.right_edge
        mpargs["west"] = gridnav.left_edge
        mpargs["south"] = gridnav.bottom_edge
        mpargs["north"] = gridnav.top_edge

    mp = MapPlot(**mpargs)

    plot_units = ""
    idx0 = hourly_offset(valid)
    ncfn = get_hourly_ncname(valid.year, domain=domain)
    if not os.path.isfile(ncfn):
        raise NoDataFound("No Data Found.")
    with ncopen(ncfn) as nc:
        cmap = get_cmap(ctx["cmap"])
        data = unit_convert(nc, varname, idx0)
        if np.ma.is_masked(np.max(data)):
            raise NoDataFound("Data Unavailable")
        ptiles = np.nanpercentile(data.filled(np.nan), [5, 95, 99.9])
        if varname in ["wind_speed"]:
            plot_units = "mph"
            clevs = pretty_bins(0, ptiles[1])
            clevs[0] = 0.01
        elif varname in [
            "p01m",
        ]:
            # Value is in W m**-2, we want MJ
            plot_units = "inch"
            if ptiles[2] < 1:
                clevs = np.arange(0, 1.01, 0.1)
            else:
                clevs = pretty_bins(0, ptiles[2])
            clevs[0] = 0.01
            cmap.set_under("white")
        elif varname in [
            "tmpk",
            "dwpk",
            "soil4t",
        ]:
            plot_units = "F"
            clevs = pretty_bins(ptiles[0], ptiles[1])
        elif varname == "rsds":
            plot_units = "W m**-2"
            clevs = pretty_bins(0, ptiles[1])

    if ptype == "c":
        x, y = np.meshgrid(gridnav.x_points, gridnav.y_points)
        # in the case of contour, use the centroids on the grids
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
