"""Comparison of hourly values for one station."""
import datetime
import calendar

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from metpy.units import units
import metpy.calc as mcalc
from pyiem.util import get_autoplot_context, get_dbconnstr
from pyiem.plot import get_cmap
from pyiem.plot import figure_axes
from pyiem.plot.util import fitbox
from pyiem.exceptions import NoDataFound

PDICT = {
    "tmpf": "Air Temperature [F]",
    "dwpf": "Dew Point Temperature [F]",
    "relh": "Relative Humidity [%]",
    "q": "Specific Humidity [g/kg]",
}
PDICT2 = {
    "no": "Plot Daily Differences",
    "yes": "Accumulate the Daily Differences",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This application presents daily comparisons of an
    automation station's hourly data.  You pick two hours of your choice and
    the application will compute the difference between the two.  The hours
    selected are for the local time zone of the station.  The comparison is
    made between the first hour and the subsequent second hour.  If the first
    hour is less than the second, the comparison is made on the same calendar
    day.  If the second hour is less than the first, then the second hour is
    taken from the next day.

    <p>The chart displays a two dimensional histogram / heatmap underneath
    the plotted lines covering the period of record data."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(type="hour", name="h1", default=6, label="First Hour:"),
        dict(
            type="hour",
            name="h2",
            default=18,
            label="Second (subsequent) Hour:",
        ),
        dict(
            type="year",
            name="y1",
            default=datetime.date.today().year,
            label="Year to highlight in chart:",
        ),
        dict(
            type="year",
            name="y2",
            default=datetime.date.today().year,
            label="Additional Year to plot (optional):",
            optional=True,
        ),
        dict(
            type="year",
            name="y3",
            default=datetime.date.today().year,
            label="Additional Year to plot (optional)",
            optional=True,
        ),
        dict(
            type="year",
            name="y4",
            default=datetime.date.today().year,
            label="Additional Year to plot (optional)",
            optional=True,
        ),
        dict(
            type="select",
            name="v",
            default="tmpf",
            label="Variable to Compare:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="opt",
            default="no",
            label="Accumulate the daily plot?",
            options=PDICT2,
        ),
        dict(
            type="int",
            name="smooth",
            default=14,
            label="Centered smooth of data over given days",
        ),
        dict(type="cmap", name="cmap", default="binary", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    h1 = int(ctx["h1"])
    h2 = int(ctx["h2"])
    varname = ctx["v"]

    tzname = ctx["_nt"].sts[station]["tzname"]

    df = read_sql(
        """
    WITH data as (
        SELECT valid at time zone %s + '10 minutes'::interval as localvalid,
        date_trunc(
             'hour', valid at time zone %s  + '10 minutes'::interval) as v,
        tmpf, dwpf, sknt, drct, alti, relh, random() as r,
        coalesce(mslp, alti * 33.8639, 1013.25) as slp
        from alldata where station = %s and report_type = 2
        and extract(hour from valid at time zone %s + '10 minutes'::interval)
        in (%s, %s)),
     agg as (
          select *, extract(hour from v) as hour,
          rank() OVER (PARTITION by v ORDER by localvalid ASC, r ASC) from data
     )

     SELECT *, date(
         case when hour = %s
         then date(v - '1 day'::interval)
         else date(v) end) from agg WHERE rank = 1
    """,
        get_dbconnstr("asos"),
        params=(
            tzname,
            tzname,
            station,
            tzname,
            h1,
            h2,
            h2 if h2 < h1 else -1,
        ),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No data was found.")
    if varname == "q":
        df["pressure"] = mcalc.add_height_to_pressure(
            df["slp"].values * units("millibars"),
            ctx["_nt"].sts[station]["elevation"] * units("m"),
        ).to(units("millibar"))
        # compute mixing ratio
        df["q"] = (
            mcalc.mixing_ratio_from_relative_humidity(
                df["pressure"].values * units("millibars"),
                df["tmpf"].values * units("degF"),
                df["relh"].values * units("percent"),
            )
            * 1000.0
        )

    # pivot
    df = df.pivot(index="date", columns="hour", values=varname).reset_index()
    df = df.dropna()
    df["doy"] = pd.to_numeric(pd.to_datetime(df["date"]).dt.strftime("%j"))
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["week"] = (df["doy"] / 7).astype(int)
    df["delta"] = df[h2] - df[h1]

    (fig, ax) = figure_axes(apctx=ctx)
    if ctx["opt"] == "no":
        ax.set_xlabel(
            "Plotted lines are smoothed over %.0f days" % (ctx["smooth"],)
        )
    ax.set_ylabel(
        "%s %s Difference"
        % (PDICT[varname], "Accumulated Sum" if ctx["opt"] == "yes" else "")
    )

    if ctx["opt"] == "no":
        # Histogram
        H, xedges, yedges = np.histogram2d(
            df["doy"].values, df["delta"].values, bins=(50, 50)
        )
        ax.pcolormesh(
            xedges,
            yedges,
            H.transpose(),
            cmap=get_cmap(ctx["cmap"]),
            alpha=0.5,
        )

    # Plot an average line
    gdf = (
        df.groupby("doy")
        .mean()
        .rolling(ctx["smooth"], min_periods=1, center=True)
        .mean()
    )
    y = gdf["delta"] if ctx["opt"] == "no" else gdf["delta"].cumsum()
    ax.plot(
        gdf.index.values,
        y,
        label="Average",
        zorder=6,
        lw=2,
        color="k",
        linestyle="-.",
    )

    # Plot selected year
    for i in range(1, 5):
        year = ctx.get(f"y{i}")
        if year is None:
            continue
        df2 = df[df["year"] == year]
        if not df2.empty:
            gdf = (
                df2.groupby("doy")
                .mean()
                .rolling(ctx["smooth"], min_periods=1, center=True)
                .mean()
            )
            y = gdf["delta"] if ctx["opt"] == "no" else gdf["delta"].cumsum()
            ax.plot(gdf.index.values, y, label=str(year), lw=2, zorder=10)

    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(1, 366)
    ax.grid(True)
    ax.legend(loc="best", ncol=5)
    sts = datetime.datetime(2000, 6, 1, h1)
    ets = datetime.datetime(2000, 6, 1, h2)
    title = (
        "%s [%s] %s Difference (%.0f-%.0f)\n" "%s minus %s (%s) (timezone: %s)"
    ) % (
        ctx["_nt"].sts[station]["name"],
        station,
        PDICT[varname],
        df["year"].min(),
        df["year"].max(),
        ets.strftime("%-I %p"),
        sts.strftime("%-I %p"),
        "same day" if h2 > h1 else "previous day",
        tzname,
    )
    fitbox(fig, title, 0.05, 0.95, 0.91, 0.99, ha="center")

    return fig, df


if __name__ == "__main__":
    plotter({})
