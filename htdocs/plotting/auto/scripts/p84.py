"""Precip estimates"""
from datetime import datetime, timedelta
import os

import numpy as np
from pyiem import iemre, util
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.reference import state_bounds, SECTORS, LATLON
from pyiem.exceptions import NoDataFound
from pyiem.util import get_dbconn, get_properties
from metpy.units import units, masked_array

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
    "yes": "Yes, overlay Drought Monitor",
    "no": "No, do not overlay Drought Monitor",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
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
      <li>Stage IV is a legacy NOAA precipitation product that gets quality
      controlled by the River Forecast Centers. This page presents
      24 hours totals at 12 UTC each day.</li>
      <li>Iowa Flood Center is an analysis produced by the U of Iowa IIHR.</li>
    </ul>
    """
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
    if src in ["mrms", "ifc"]:
        # This is generally closer to 'daily
        if sdate == edate:
            title = sdate.strftime("%-d %B %Y")
        else:
            title = f"{sdate:%-d %b} to {edate:%-d %b %Y} (inclusive)"
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


def get_ugc_bounds(ctx, sector):
    """Do custom bounds stuff."""
    if ctx.get("ugc") is None:
        return sector, "", 0, 0, 0, 0
    cursor = get_dbconn("postgis").cursor()
    cursor.execute(
        "SELECT st_xmin(geom), st_xmax(geom), st_ymin(geom), st_ymax(geom), "
        "name from ugcs WHERE ugc = %s and end_ts is null",
        (ctx["ugc"],),
    )
    if cursor.rowcount == 0:
        return sector, "", 0, 0, 0, 0
    row = cursor.fetchone()
    b = 0.15  # arb
    return (
        "custom",
        row[4],
        row[0] - b,
        row[3] + b,
        row[1] + b,
        row[2] - b,
    )


def plotter(fdict):
    """Go"""
    ctx = util.get_autoplot_context(fdict, get_description())
    ptype = ctx["ptype"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    src = ctx["src"]
    opt = ctx["opt"]
    usdm = ctx["usdm"]
    if sdate.year != edate.year:
        raise NoDataFound("Sorry, do not support multi-year plots yet!")
    sector = ctx["sector"]

    x0 = 0
    x1 = -1
    y0 = 0
    y1 = -1
    state = None
    if len(sector) == 2:
        state = sector
        sector = "state"

    clncvar = "p01d"
    if src == "mrms":
        ncfn = iemre.get_daily_mrms_ncname(sdate.year)
        clncfn = iemre.get_dailyc_mrms_ncname()
        ncvar = "p01d"
        source = "MRMS Q3"
        subtitle = "NOAA MRMS Project, MultiSensorPass2 and RadarOnly"
    elif src == "iemre":
        ncfn = iemre.get_daily_ncname(sdate.year)
        clncfn = iemre.get_dailyc_ncname()
        ncvar = "p01d_12z"
        clncvar = "p01d"
        source = "IEM Reanalysis"
        subtitle = "IEM Reanalysis is derived from various NOAA datasets"
    elif src == "ifc":
        ncfn = f"/mesonet/data/iemre/{sdate.year}_ifc_daily.nc"
        clncfn = "/mesonet/data/iemre/ifc_dailyc.nc"
        ncvar = "p01d"
        source = "Iowa Flood Center (Iowa Only)"
        subtitle = "IFC analysis courtesy of U of Iowa IIHR"
    elif src == "stage4":
        ncfn = f"/mesonet/data/stage4/{sdate.year}_stage4_daily.nc"
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
        edate = min([archive_end, edate])
        ncfn = "/mesonet/data/prism/%s_daily.nc" % (sdate.year,)
        clncfn = "/mesonet/data/prism/prism_dailyc.nc"
        ncvar = "ppt"
        clncvar = "ppt"
        source = "OSU PRISM"
        subtitle = (
            "PRISM Climate Group, Oregon State Univ., "
            "http://prism.oregonstate.edu, created 4 Feb 2004."
        )
    # important to do here after fixing the edate above
    title = compute_title(src, sdate, edate)

    sector, name, west, north, east, south = get_ugc_bounds(ctx, sector)
    if ctx.get("ugc") is not None:
        subtitle += f", zoomed on [{ctx['ugc']}] {name}"

    mp = MapPlot(
        sector=sector,
        state=state,
        north=north,
        east=east,
        south=south,
        west=west,
        axisbg="white",
        nocaption=True,
        title=f"{source}:: {title} Precip {PDICT3[opt]}",
        subtitle=f"Data from {subtitle}",
        titlefontsize=14,
        apctx=ctx,
    )
    (west, east, south, north) = mp.panels[0].get_extent(LATLON)

    idx0 = iemre.daily_offset(sdate)
    idx1 = iemre.daily_offset(edate) + 1
    if not os.path.isfile(ncfn):
        raise NoDataFound("No data for that year, sorry.")
    with util.ncopen(ncfn) as nc:
        if sector == "custom":
            x0, y0, x1, y1 = util.grid_bounds(
                nc.variables["lon"][:],
                nc.variables["lat"][:],
                [west, south, east, north],
            )
        elif state is not None:
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
        if src == "stage4":
            lats = nc.variables["lat"][y0:y1, x0:x1]
            lons = nc.variables["lon"][y0:y1, x0:x1]
        else:
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
                np.sum(nc.variables[clncvar][idx0:idx1, y0:y1, x0:x1], 0)
            )
        p01d = p01d - climo
        [maxv] = np.percentile(np.abs(p01d), [99])
        clevs = np.around(np.linspace(0 - maxv, maxv, 11), decimals=2)
    elif opt == "per":
        with util.ncopen(clncfn) as nc:
            climo = mm2inch(
                np.sum(nc.variables[clncvar][idx0:idx1, y0:y1, x0:x1], 0)
            )
        p01d = p01d / climo * 100.0
        clevs = [1, 10, 25, 50, 75, 100, 125, 150, 200, 300, 500]
        plot_units = "percent"
    else:
        p01d = np.where(p01d < 0.001, np.nan, p01d)
        cmap.set_under("white")
        # Dynamic Range based on min/max grid value, since we restrict plot
        minval = np.floor(np.nanmin(p01d))
        maxval = np.ceil(np.percentile(p01d, [95])[0])
        clevs = [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
        if minval == 0:
            if maxval <= 1:
                clevs = np.arange(0, 1.01, 0.1)
            elif maxval <= 3:
                clevs = np.arange(0, 3.01, 0.25)
            elif maxval <= 5:
                clevs = np.arange(0, 5.01, 0.5)
            elif maxval <= 10:
                clevs = np.arange(0, 10.01, 1.0)
        else:
            # Find an interval that encloses the bounds
            rng = maxval - minval
            for interval in [0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5, 10]:
                if interval * 10 >= rng:
                    clevs = np.arange(
                        minval, minval + interval * 10 + 0.01, interval
                    )
                    break
        if minval == 0:
            clevs[0] = 0.01

    if len(lons.shape) == 1:
        x2d, y2d = np.meshgrid(lons, lats)
    else:
        x2d, y2d = lons, lats
    if ptype == "c":
        mp.contourf(
            x2d,
            y2d,
            p01d,
            clevs,
            cmap=cmap,
            units=plot_units,
            iline=False,
            clip_on=False,
        )
    else:
        res = mp.pcolormesh(
            x2d,
            y2d,
            p01d,
            clevs,
            cmap=cmap,
            units=plot_units,
            clip_on=False,
        )
        res.set_rasterized(True)
    if sector not in ["midwest", "conus"]:
        mp.drawcounties()
        mp.drawcities(minpop=500 if sector == "custom" else 5000)
    if usdm == "yes":
        mp.draw_usdm(edate, filled=False, hatched=True)

    return mp.fig


if __name__ == "__main__":
    plotter(dict(sdate="2019-01-01", edate="2019-02-01", src="stage4"))
