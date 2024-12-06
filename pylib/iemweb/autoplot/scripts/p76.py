"""
Simple plot of yearly average dew points by year,
season, or month.
This calculation was done by computing the mixing ratio, then averaging
the mixing ratios by year, and then converting that average to a dew point.
This was done due to the non-linear nature of dew point when expressed in
units of temperature.  If you plot the 'winter' season, the year shown is
of the Jan/Feb portion of the season. If you plot the 'Water Year', the
year shown is the September 30th of the period.

<p>You can optionally restrict the local hours of the day to consider for
the plot.  These hours are expressed as a range of hours using a 24 hour
clock.  For example, '8-16' would indicate a period between 8 AM and 4 PM
inclusive.  If you want to plot one hour, just set the start and end hour
to the same value.</p>
"""

import datetime

import metpy.calc as mcalc
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from metpy.units import units
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, utc
from scipy import stats
from sqlalchemy import text

from iemweb.util import month2months

MDICT = {
    "all": "No Month/Time Limit",
    "water_year": "Water Year",
    "spring": "Spring (MAM)",
    "spring2": "Spring (AMJ)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}
PDICT = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "feel": "Feels Like Temperature",
    "relh": "Relative Humidity",
    "vpd": "Vapor Pressure Deficit",
}
UNITS = {
    "tmpf": "F",
    "dwpf": "F",
    "feel": "F",
    "relh": "%",
    "vpd": "hPa",
}
PDICT2 = {
    "bar": "Bar Plot",
    "violin": "Violin Plot",
}
PDICT3 = {
    "min": "Minimum",
    "mean": "Mean",
    "max": "Maximum",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="DSM",
            label="Select Station",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="season",
            default="winter",
            label="Select Time Period:",
            options=MDICT,
        ),
        dict(
            type="select",
            name="varname",
            default="dwpf",
            label="Metric to Plot:",
            options=PDICT,
        ),
        {
            "type": "select",
            "options": PDICT3,
            "default": "mean",
            "label": "Daily aggregate to use in yearly statistics",
            "name": "agg",
        },
        dict(
            type="year", name="year", default=1893, label="Start Year of Plot"
        ),
        dict(
            type="select",
            name="w",
            default="violin",
            label="Select plot type",
            options=PDICT2,
        ),
        dict(
            type="text",
            name="hours",
            optional=True,
            default="0-23",
            label=(
                "Inclusive Local Hours (24-hour clock) "
                "to Limit Analysis (optional)"
            ),
        ),
    ]
    return desc


def run_calcs(df, ctx):
    """Do our maths."""
    # Convert sea level pressure to station pressure
    df["pressure"] = (
        mcalc.add_height_to_pressure(
            df["slp"].values * units("millibars"),
            ctx["_nt"].sts[ctx["station"]]["elevation"] * units("m"),
        )
        .to(units("millibar"))
        .m
    )
    # Compute the mixing ratio
    df["mixingratio"] = mcalc.mixing_ratio_from_relative_humidity(
        df["pressure"].values * units("millibars"),
        df["tmpf"].values * units("degF"),
        df["relh"].values * units("percent"),
    ).m
    # Compute the saturation mixing ratio
    df["saturation_mixingratio"] = mcalc.saturation_mixing_ratio(
        df["pressure"].values * units("millibars"),
        df["tmpf"].values * units("degF"),
    ).m
    df["vapor_pressure"] = (
        mcalc.vapor_pressure(
            df["pressure"].values * units("millibars"),
            df["mixingratio"].values * units("kg/kg"),
        )
        .to(units("hPa"))
        .m
    )
    df["saturation_vapor_pressure"] = (
        mcalc.vapor_pressure(
            df["pressure"].values * units("millibars"),
            df["saturation_mixingratio"].values * units("kg/kg"),
        )
        .to(units("hPa"))
        .m
    )
    df["vpd"] = df["saturation_vapor_pressure"] - df["vapor_pressure"]
    # remove any NaN rows
    df = df.dropna()
    return df


def get_data(ctx, startyear):
    """Get data"""
    today = datetime.datetime.now()
    lastyear = today.year
    deltadays = 0
    months = month2months(ctx["season"])
    if ctx["season"] == "water_year":
        deltadays = 92
        lastyear += 1
    elif ctx["season"] == "spring":
        if today.month > 5:
            lastyear += 1
    elif ctx["season"] == "spring2":
        if today.month > 6:
            lastyear += 1
    elif ctx["season"] == "fall":
        if today.month > 11:
            lastyear += 1
    elif ctx["season"] == "summer":
        if today.month > 8:
            lastyear += 1
    elif ctx["season"] == "winter":
        deltadays = 33
        if today.month > 2:
            lastyear += 1
    else:
        lastyear += 1
    if startyear >= lastyear:
        raise NoDataFound("Start year should be less than end year.")
    hours = list(range(24))
    if ctx.get("hours"):
        try:
            tokens = [int(i.strip()) for i in ctx["hours"].split("-")]
            hours = list(range(tokens[0], tokens[1] + 1))
        except ValueError as exp:
            raise Exception("malformed hour limiter, sorry.") from exp
        ctx["hour_limiter"] = (
            f"[{utc(2017, 1, 1, tokens[0]):%-I %p}-"
            f"{utc(2017, 1, 1, tokens[1]):%-I %p}]"
        )
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                """
            WITH obs as (
                SELECT valid at time zone :tzname as valid, tmpf, dwpf, relh,
                coalesce(mslp, alti * 33.8639, 1013.25) as slp,
                coalesce(feel, tmpf) as feel
                from alldata WHERE station = :station and dwpf > -90
                and dwpf < 100 and tmpf >= dwpf and
                extract(month from valid) = ANY(:months) and
                extract(hour from valid at time zone :tzname) = ANY(:hours)
                and report_type = 3
            )
        SELECT valid,
        date(valid at time zone :tzname),
        extract(year from valid + ':days days'::interval)::int as year,
        tmpf, dwpf, slp, relh, feel from obs
        """
            ),
            conn,
            params={
                "tzname": ctx["_nt"].sts[ctx["station"]]["tzname"],
                "station": ctx["station"],
                "months": months,
                "hours": hours,
                "days": deltadays,
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data found.")
    df = df[(df["year"] >= startyear) & (df["year"] < lastyear)]
    return df


def make_plot(df, ctx):
    """Do the plotting"""

    means = (
        df.groupby("date")
        .agg(ctx["agg"], numeric_only=True)
        .reset_index()
        .groupby("year")
        .mean(numeric_only=True)
    )
    # Special case of computing means of non-linear dew point
    means["dwpf"] = (
        mcalc.dewpoint(means["vapor_pressure"].values * units("hPa"))
        .to(units("degF"))
        .m
    )
    if means.empty:
        raise NoDataFound("No data found.")

    season = ctx["season"]
    varname = ctx["varname"]
    h_slope, intercept, r_value, _, _ = stats.linregress(
        means.index.values, means[varname].values
    )
    avgv = means[varname].mean()
    tt = "Distribution" if ctx["w"] == "violin" else "Averages"
    title = (
        f"{ctx['_sname']} ({means.index.min():.0f}-{means.index.max():.0f})\n"
        f"{PDICT3[ctx['agg']]} Daily {PDICT[varname]} {tt} [{MDICT[season]}] "
        f"{ctx.get('hour_limiter', '')} Avg: {avgv:.1f}, "
        f"slope: {(h_slope * 100.):.2f} {UNITS[varname]}/century, "
        f"R$^2$={(r_value**2):.2f}"
    )

    (fig, ax) = figure_axes(title=title, apctx=ctx)

    ar = ["tmpf", "relh", "dwpf", "feel"]
    colorabove = "seagreen" if varname in ar else "lightsalmon"
    colorbelow = "lightsalmon" if varname in ar else "seagreen"
    if ctx["w"] == "bar":
        cols = ax.bar(
            means.index.values,
            means[varname].values,
            fc=colorabove,
            ec=colorabove,
            align="center",
        )
        for i, col in enumerate(cols):
            if means.iloc[i][varname] < avgv:
                col.set_facecolor(colorbelow)
                col.set_edgecolor(colorbelow)
        ax.set_ylim(
            0 if varname == "vpd" else (means[varname].min() - 5),
            means[varname].max() + means[varname].max() / 10.0,
        )
    else:
        data = (
            df.groupby("date")
            .agg(ctx["agg"], numeric_only=True)
            .reset_index()
            .groupby("year")[varname]
            .apply(list)
        )
        v1 = ax.violinplot(
            data.values,
            positions=list(data.index),
            showextrema=True,
            showmeans=True,
            widths=1.5,
        )
        for i, b in enumerate(v1["bodies"]):
            m = np.mean(b.get_paths()[0].vertices[:, 0])
            # modify the paths to not go further left than the center
            b.get_paths()[0].vertices[:, 0] = np.clip(
                b.get_paths()[0].vertices[:, 0], m, np.inf
            )
            if means.iloc[i][varname] < avgv:
                b.set_color(colorbelow)
            else:
                b.set_color(colorabove)
    ax.axhline(avgv, lw=2, color="k", zorder=2, label="Average")
    ax.plot(
        means.index.values,
        h_slope * means.index.values + intercept,
        "--",
        lw=2,
        color="k",
        label="Trend",
    )
    ax.set_xlabel("Year")
    ax.set_xlim(means.index.min() - 1, means.index.max() + 1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel(f"{PDICT[varname]} [{UNITS[varname]}]")
    ax.grid(True)
    ax.legend(ncol=2)
    return fig, means


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    startyear = ctx["year"]

    df = get_data(ctx, startyear)
    df = run_calcs(df, ctx)
    fig, means = make_plot(df, ctx)

    return fig, means
