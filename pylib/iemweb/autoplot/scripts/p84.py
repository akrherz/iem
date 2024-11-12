"""
This application generates maps of precipitation
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
    <li><a href="https://prism.oregonstate.edu">Oregon State PRISM</a>
    <br />The PRISM data is credit Oregon State University,
    created 4 Feb 2004.  This information arrives with a few day lag. The
    plotted totals represent periods typical to COOP data reporting, so
    12 UTC (7 AM local) each day.</li>
    <li>Stage IV is a legacy NOAA precipitation product that gets quality
    controlled by the River Forecast Centers. This page presents
    24 hours totals at 12 UTC each day.</li>
    <li>Iowa Flood Center is an analysis produced by the U of Iowa IIHR.</li>
</ul>
"""

import os
from datetime import datetime, timedelta

import numpy as np
from metpy.units import masked_array, units
from pyiem import iemre, util
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import get_cmap, pretty_bins
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import LATLON
from pyiem.util import get_properties

PDICT2 = {"c": "Contour Plot", "g": "Grid Cell Mesh"}
SRCDICT = {
    "iemre": "IEM Reanalysis (since 1 Jan 1893)",
    "ifc": "Iowa Flood Center (since 1 Jan 2016) [Iowa-Only]",
    "mrms": "NOAA MRMS (since 1 Jan 2001)",
    "prism": "OSU PRISM (since 1 Jan 1981)",
    "stage4": "Stage IV (since 1 Apr 1998)",
}
PDICT3 = {
    "acc": "Accumulation",
    "dep": "Departure from Average [inch]",
    "per": "Percent of Average [%]",
}
PDICT4 = {
    "yes": "Yes, overlay Drought Monitor (valid near end date)",
    "yesb": "Yes, overlay Drought Monitor (valid near begin date)",
    "no": "No, do not overlay Drought Monitor",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": False}
    desc["cache"] = 3600  # Things like MRMS update hourly
    today = datetime.today() - timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="csector", name="sector", default="IA", label="Select Sector:"
        ),
        dict(
            type="ugc",
            name="ugc",
            default="IAC153",
            label="Plot zoomed in on given County/Parish/Forecast Zone:",
            optional=True,
        ),
        dict(
            type="networkselect",
            name="cwa",
            default="DMX",
            label="Plot for CONUS NWS WFO",
            optional=True,
            network="WFO",
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
            max=f"{datetime.today():%Y/%m/%d}",
        ),
        dict(type="cmap", name="cmap", default="YlGnBu", label="Color Ramp:"),
    ]
    return desc


def mm2inch(val):
    """Helper."""
    return masked_array(val, units("mm")).to(units("inch")).m


def compute_title(src, sdate, edate):
    """Figure out how to label this fun."""
    if src in ["mrms", "ifc"]:
        # This is generally closer to 'daily
        if sdate == edate:
            title = sdate.strftime("%-d %B %Y")
        else:
            title = (
                f"{sdate:%-d %b} to {edate:%-d %b %Y} (US Central, inclusive)"
            )
    else:
        # This is 12z to 12z totals.
        if sdate == edate:
            title = (
                f"{(sdate - timedelta(days=1)):%-d %B %Y} ~12z to "
                f"{edate:%-d %B %Y} ~12z"
            )
        else:
            title = (
                f"{(sdate - timedelta(days=1)):%-d %B %Y} ~12z to "
                f"{(edate + timedelta(days=1)):%-d %B %Y} ~12z"
            )
    return title


def get_ugc_bounds(ctx, sector):
    """Do custom bounds stuff."""
    if ctx.get("ugc") is None:
        return sector, "", 0, 0, 0, 0
    conn, cursor = get_dbconnc("postgis")
    cursor.execute(
        "SELECT st_xmin(geom), st_xmax(geom), st_ymin(geom), st_ymax(geom), "
        "name from ugcs WHERE ugc = %s and end_ts is null",
        (ctx["ugc"],),
    )
    if cursor.rowcount == 0:
        return sector, "", 0, 0, 0, 0
    row = cursor.fetchone()
    conn.close()
    b = 0.15  # arb
    return (
        "custom",
        row["name"],
        row["st_xmin"] - b,
        row["st_ymax"] + b,
        row["st_xmax"] + b,
        row["st_ymin"] - b,
    )


def set_ncinfo(ctx):
    """Define the netcdf stuff we need."""
    clncvar = "p01d"
    if ctx["src"] == "mrms":
        ncfn = iemre.get_daily_mrms_ncname(ctx["sdate"].year)
        clncfn = iemre.get_dailyc_mrms_ncname()
        ncvar = "p01d"
        source = "MRMS Q3"
        subtitle = "NOAA MRMS Project, MultiSensorPass2 and RadarOnly"
    elif ctx["src"] == "iemre":
        ncfn = iemre.get_daily_ncname(ctx["sdate"].year)
        clncfn = iemre.get_dailyc_ncname()
        ncvar = "p01d_12z"
        clncvar = "p01d"
        source = "IEM Reanalysis"
        subtitle = "IEM Reanalysis is derived from various NOAA datasets"
    elif ctx["src"] == "ifc":
        ncfn = f"/mesonet/data/iemre/{ctx['sdate'].year}_ifc_daily.nc"
        clncfn = "/mesonet/data/iemre/ifc_dailyc.nc"
        ncvar = "p01d"
        source = "Iowa Flood Center (Iowa Only)"
        subtitle = "IFC analysis courtesy of U of Iowa IIHR"
    elif ctx["src"] == "stage4":
        ncfn = f"/mesonet/data/stage4/{ctx['sdate'].year}_stage4_daily.nc"
        clncfn = "/mesonet/data/stage4/stage4_dailyc.nc"
        ncvar = "p01d_12z"
        clncvar = "p01d_12z"
        source = "NOAA StageIV"
        subtitle = "NOAA/NWS River Forecast Centers"
    else:
        # Threshold edate
        archive_end = datetime.strptime(
            get_properties().get("prism.archive_end", "1980-01-01"),
            "%Y-%m-%d",
        ).date()
        ctx["edate"] = min([archive_end, ctx["edate"]])
        ctx["sdate"] = min([ctx["edate"], ctx["sdate"]])
        ncfn = f"/mesonet/data/prism/{ctx['sdate'].year}_daily.nc"
        clncfn = "/mesonet/data/prism/prism_dailyc.nc"
        ncvar = "ppt"
        clncvar = "ppt"
        source = "OSU PRISM"
        subtitle = (
            "PRISM Climate Group, Oregon State Univ., "
            "http://prism.oregonstate.edu, created 4 Feb 2004."
        )
    ctx["ncfn"] = ncfn
    ctx["clncfn"] = clncfn
    ctx["ncvar"] = ncvar
    ctx["clncvar"] = clncvar
    ctx["source"] = source
    ctx["subtitle"] = subtitle


def set_gridinfo(ctx):
    """Do the grid info work."""
    idx0 = iemre.daily_offset(ctx["sdate"])
    idx1 = iemre.daily_offset(ctx["edate"]) + 1
    if not os.path.isfile(ctx["ncfn"]):
        raise NoDataFound("No data for that year, sorry.")
    with util.ncopen(ctx["ncfn"]) as nc:
        x0, y0, x1, y1 = util.grid_bounds(
            nc.variables["lon"][:],
            nc.variables["lat"][:],
            [ctx["west"], ctx["south"], ctx["east"], ctx["north"]],
        )
        if ctx["sector"] == "conus":
            x0, y0, x1, y1 = 0, 0, -1, -1
        if ctx["src"] == "stage4":
            lats = nc.variables["lat"][y0:y1, x0:x1]
            lons = nc.variables["lon"][y0:y1, x0:x1]
        else:
            lats = nc.variables["lat"][y0:y1]
            lons = nc.variables["lon"][x0:x1]
        if ctx["sdate"] == ctx["edate"]:
            p01d = mm2inch(nc.variables[ctx["ncvar"]][idx0, y0:y1, x0:x1])
        elif (idx1 - idx0) < 32:
            p01d = mm2inch(
                np.nansum(
                    nc.variables[ctx["ncvar"]][idx0:idx1, y0:y1, x0:x1], 0
                )
            )
        else:
            # Too much data can overwhelm this app, need to chunk it
            for i in range(idx0, idx1, 10):
                i2 = min([i + 10, idx1])
                if idx0 == i:
                    p01d = mm2inch(
                        np.nansum(
                            nc.variables[ctx["ncvar"]][i:i2, y0:y1, x0:x1], 0
                        )
                    )
                else:
                    p01d += mm2inch(
                        np.nansum(
                            nc.variables[ctx["ncvar"]][i:i2, y0:y1, x0:x1], 0
                        )
                    )
    ctx["lats"] = lats
    ctx["lons"] = lons
    ctx["p01d"] = p01d
    ctx["idx0"] = idx0
    ctx["idx1"] = idx1
    ctx["x0"] = x0
    ctx["y0"] = y0
    ctx["x1"] = x1
    ctx["y1"] = y1


def set_data(ctx):
    """Do the data work."""
    if 0 in ctx["p01d"].shape:
        raise NoDataFound("No data found for this period")
    if np.ma.is_masked(np.max(ctx["p01d"])):
        raise NoDataFound("Data was found, but all missing")
    p01d = ctx["p01d"].filled(np.nan)
    plot_units = "inches"
    cmap = get_cmap(ctx["cmap"])
    cmap.set_bad("white")
    tslice = slice(ctx["idx0"], ctx["idx1"])
    yslice = slice(ctx["y0"], ctx["y1"])
    xslice = slice(ctx["x0"], ctx["x1"])
    if ctx["opt"] == "dep":
        # Do departure work now
        with util.ncopen(ctx["clncfn"]) as nc:
            climo = mm2inch(
                np.sum(nc.variables[ctx["clncvar"]][tslice, yslice, xslice], 0)
            )
        p01d = p01d - climo
        [maxv] = np.nanpercentile(np.abs(p01d), [99])
        clevs = np.around(np.linspace(0 - maxv, maxv, 11), decimals=2)
    elif ctx["opt"] == "per":
        with util.ncopen(ctx["clncfn"]) as nc:
            climo = mm2inch(
                np.sum(nc.variables[ctx["clncvar"]][tslice, yslice, xslice], 0)
            )
        p01d = p01d / climo * 100.0
        clevs = [1, 10, 25, 50, 75, 100, 125, 150, 200, 300, 500]
        plot_units = "percent"
    else:
        p01d = np.where(p01d < 0.001, np.nan, p01d)
        cmap.set_under("white")
        # Dynamic Range based on min/max grid value, since we restrict plot
        maxval = np.ceil(np.nanpercentile(p01d, [99])[0])
        if np.isnan(maxval) or maxval < 1:
            clevs = np.arange(0, 1.01, 0.1)
        else:
            clevs = pretty_bins(0, maxval)
        clevs[0] = 0.01

    if len(ctx["lons"].shape) == 1:
        x2d, y2d = np.meshgrid(ctx["lons"], ctx["lats"])
    else:
        x2d, y2d = ctx["lons"], ctx["lats"]

    ctx["clevs"] = clevs
    ctx["p01d"] = p01d
    ctx["plot_units"] = plot_units
    ctx["cmap"] = cmap
    ctx["x2d"] = x2d
    ctx["y2d"] = y2d


def set_mapplot(ctx):
    """Setup the mapplot instance."""
    state = None
    sector = ctx["sector"]
    if len(ctx["sector"]) == 2:
        state = ctx["sector"]
        sector = "state"
    if ctx.get("cwa") is not None:
        sector = "cwa"
    ctx["sector"], name, west, north, east, south = get_ugc_bounds(ctx, sector)
    if ctx["sector"] == "iowa":
        ctx["sector"] = "state"
        state = "IA"
    if ctx.get("ugc") is not None:
        ctx["subtitle"] += f", zoomed on [{ctx['ugc']}] {name}"
    title = compute_title(ctx["src"], ctx["sdate"], ctx["edate"])
    ctx["mp"] = MapPlot(
        sector=ctx["sector"],
        cwa=ctx.get("cwa"),
        state=state,
        north=north,
        east=east,
        south=south,
        west=west,
        axisbg="white",
        nocaption=True,
        title=f"{ctx['source']}:: {title} Precip {PDICT3[ctx['opt']]}",
        subtitle=f"Data from {ctx['subtitle']}",
        titlefontsize=14,
        apctx=ctx,
    )
    ctx["west"], ctx["east"], ctx["south"], ctx["north"] = (
        ctx["mp"].panels[0].get_extent(LATLON)
    )


def finalize_map(ctx):
    """Finish it."""
    if ctx["ptype"] == "c":
        ctx["mp"].contourf(
            ctx["x2d"],
            ctx["y2d"],
            ctx["p01d"],
            ctx["clevs"],
            cmap=ctx["cmap"],
            units=ctx["plot_units"],
            iline=False,
            clip_on=False,
        )
    else:
        res = ctx["mp"].pcolormesh(
            ctx["x2d"],
            ctx["y2d"],
            ctx["p01d"],
            ctx["clevs"],
            cmap=ctx["cmap"],
            units=ctx["plot_units"],
            clip_on=False,
        )
        res.set_rasterized(True)
    if (ctx["east"] - ctx["west"]) < 10:
        ctx["mp"].drawcounties()
        ctx["mp"].drawcities(minpop=500 if ctx["sector"] == "custom" else 5000)
    if ctx["usdm"].startswith("yes"):
        ctx["mp"].draw_usdm(
            ctx["edate"] if ctx["usdm"] == "yes" else ctx["sdate"],
            filled=False,
            hatched=True,
        )
    if ctx.get("cwa") is not None:
        ctx["mp"].draw_cwas()
    ctx["mp"].draw_mask("conus")


def plotter(fdict):
    """Go"""
    ctx = util.get_autoplot_context(fdict, get_description())
    if ctx["sdate"] > ctx["edate"]:
        ctx["sdate"], ctx["edate"] = ctx["edate"], ctx["sdate"]
    if ctx["sdate"].year != ctx["edate"].year:
        raise NoDataFound("Sorry, do not support multi-year plots yet!")

    set_ncinfo(ctx)
    set_mapplot(ctx)
    set_gridinfo(ctx)
    set_data(ctx)
    finalize_map(ctx)

    return ctx["mp"].fig
