"""
This plot presents a climatology of wind
observations.  The top panel presents the u (east/west) and v (north/south)
components.  The bottom panel is the simple average of the wind speed
magnitude.  The plotted information contains a seven day smoother.  If you
download the raw data, it will not contain this smoothing.
"""

import calendar
import datetime

import numpy as np
import pandas as pd
from metpy.calc import wind_components
from metpy.units import units
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "mps": "Meters per Second",
    "kt": "Knots",
    "kmh": "Kilometers per Hour",
    "mph": "Miles per Hour",
}
XREF_UNITS = {
    "mps": units("meter / second"),
    "kt": units("knot"),
    "kmh": units("kilometer / hour"),
    "mph": units("mile / hour"),
}


def smooth(x):
    """Smooth the data"""
    return pd.Series(x).rolling(7, min_periods=1).mean()


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="units",
            default="mph",
            label="Wind Speed Units:",
            options=PDICT,
        ),
    ]
    return desc


def add_plot(ctx):
    """Do plotting."""
    title = (
        f"{ctx['_sname']} :: Daily Average Component Wind Speed\n"
        f"[{ctx['ab'].year}-{datetime.datetime.now().year}] 7 day smooth "
        f"filter applied, {len(ctx['df'].index):.0f} obs found"
    )
    ctx["fig"] = figure(apctx=ctx, title=title)
    axes = ctx["fig"].subplots(2, 1)
    ax = axes[0]
    ax.plot(
        np.arange(1, len(ctx["u"])),
        smooth(ctx["u"][:-1]),
        color="r",
        label="u, West(+) : East(-) component",
        lw=2,
    )
    ax.plot(
        np.arange(1, len(ctx["v"])),
        smooth(ctx["v"][:-1]),
        color="b",
        label="v, South(+) : North(-) component",
        lw=2,
    )
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.legend(ncol=2, fontsize=11, loc=(0.0, -0.25))
    ax.grid(True)
    ax.set_xlim(0, 366)
    ax.set_ylabel(f"Average Wind Speed\n{PDICT.get(ctx['units'])}")

    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
    )

    ax = axes[1]
    ax.plot(
        np.arange(1, len(ctx["mag"])),
        smooth(ctx["mag"][:-1]),
        color="g",
        lw=2,
        label="Speed Magnitude",
    )
    ax.legend(loc="best")
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_ylabel(f"Average Wind Speed\n{PDICT[ctx['units']]}")
    ax.grid(True)
    ax.set_xlim(0, 366)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["ab"] = ctx["_nt"].sts[ctx["station"]]["archive_begin"]
    if ctx["ab"] is None:
        raise NoDataFound("Unknown station metadata.")
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            "SELECT extract(doy from valid) as doy, sknt, drct from alldata "
            "where station = %s and sknt >= 0 and drct >= 0 "
            "and report_type = 3",
            conn,
            params=(ctx["station"],),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data Found.")

    # Compute components in MPS
    u, v = wind_components(
        (df["sknt"].values * units("knot")).to(units("meter / second")),
        df["drct"].values * units("degree"),
    )
    df["u"] = u.m
    df["v"] = v.m
    gdf = df.groupby(by="doy").mean()
    ctx["u"] = (
        (gdf["u"].values * units("meter / second"))
        .to(XREF_UNITS[ctx["units"]])
        .m
    )
    ctx["v"] = (
        (gdf["v"].values * units("meter / second"))
        .to(XREF_UNITS[ctx["units"]])
        .m
    )
    ctx["mag"] = (
        (gdf["sknt"].values * units("knot")).to(XREF_UNITS[ctx["units"]]).m
    )

    df2 = pd.DataFrame(
        dict(
            u=pd.Series(u),
            v=pd.Series(v),
            mag=pd.Series(ctx["mag"]),
            day_of_year=pd.Series(np.arange(1, 367)),
        )
    )
    ctx["df"] = df
    add_plot(ctx)
    return ctx["fig"], df2
