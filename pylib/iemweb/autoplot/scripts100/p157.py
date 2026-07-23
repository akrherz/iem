"""
Based on available hourly or better observations, the IEM computes local
calendar day statistics for variables like relative humidity, dew point,
and feels like (read: windchill or heat index) temperature.  This autoplot
computes a simple climatology of these values with a smoothing to remove some
of the day to day variability.

<p>Note that the observations plotted can fall outside of the smoothed range of
values, as the smoothing is applied to the climatology and not the individual
observations.
"""

from datetime import datetime, timedelta

import pandas as pd
from matplotlib.axes import Axes
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

PDICT = {"above": "Above Threshold", "below": "Below Threshold"}
PDICT2 = {
    "max_rh": "Daily Max RH",
    "avg_rh": "Daily Avg RH",
    "min_rh": "Daily Min RH",
    "max_dwpf": "Daily Max Dew Point",
    "min_dwpf": "Daily Min Dew Point",
    "max_feel": "Daily Max Feels Like",
    "avg_feel": "Daily Avg Feels Like",
    "min_feel": "Daily Min Feels Like",
}

OBS_STYLES = (
    {"color": "#111111", "marker": "o"},
    {"color": "#8B1E3F", "marker": "D"},
)


def xlabel_magic(ax: Axes, sday, eday):
    """Figure out how to nicely label the faked dates on the axis."""
    number_of_days = (eday - sday).total_seconds() / (24 * 60 * 60)
    # Life choices
    days = [
        1,
    ]
    if number_of_days < 60:
        days = [1, 8, 15, 22, 29]
    elif number_of_days < 190:
        days = [1, 15]
    xticks = []
    xticklabels = []
    for dt in pd.date_range(sday, eday):
        if dt.day in days:
            xticks.append(dt)
            xticklabels.append(dt.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.today() - timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="DSM",
            label="Select Station",
            network="IA_ASOS",
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Plot this year's observations:",
        ),
        {
            "type": "year",
            "name": "y2",
            "default": today.year - 1,
            "label": "Optionally, also plot this year's observations:",
            "optional": True,
        },
        dict(
            type="select",
            name="var",
            options=PDICT2,
            default="max_rh",
            label="Which Variable",
        ),
        dict(
            type="select",
            name="dir",
            options=PDICT,
            default="above",
            label="Threshold Direction",
        ),
        dict(
            type="int",
            name="thres",
            default=95,
            label="Threshold [%,°F] for Frequency",
        ),
        {
            "type": "int",
            "name": "smooth",
            "default": 7,
            "label": "Smoothing Window Size (days), 1 disables, max 60",
        },
        {
            "type": "sday",
            "name": "sday",
            "default": "0101",
            "label": "Start Day of the Year for Plotting",
        },
        {
            "type": "sday",
            "name": "eday",
            "default": "1231",
            "label": "End Day of the Year for Plotting",
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    threshold = ctx["thres"]
    mydir = ctx["dir"]
    varname = ctx["var"]
    smooth = ctx["smooth"]
    sday = pd.to_datetime(ctx["sday"])
    eday = pd.to_datetime(ctx["eday"])
    if sday >= eday:
        raise ValueError("Plots crossing 1 Jan are not supported, yet")
    if smooth < 1 or smooth > 60:
        raise ValueError("Invalid smoothing window size, must be 1-60")

    op = ">=" if mydir == "above" else "<"
    with get_sqlalchemy_conn("iem") as conn:
        obsdf = pd.read_sql(
            sql_helper(
                """
            SELECT day, {varname},
            case when {varname} {op} :threshold then 1 else 0 end
            as threshold_exceed from summary s WHERE iemid = :iemid
            and {varname} is not null ORDER by day ASC
        """,
                varname=varname,
                op=op,
            ),
            conn,
            params={
                "threshold": threshold,
                "iemid": ctx["_nt"].sts[station]["iemid"],
            },
            index_col="day",
            parse_dates="day",
        )
    if obsdf.empty:
        raise NoDataFound("No Data Found.")

    # Since doy is a poor choice for multi-year plotting, we create a faked
    # year 2000 date for each entry
    obsdf["plotdate"] = obsdf.index.map(lambda ts: ts.replace(year=2000))
    bydate = (
        obsdf[["plotdate", varname]]
        .groupby("plotdate")
        .describe()
        .rolling(window=smooth, center=True)
        .mean()
    )
    # Drop the multi-index column
    bydate.columns = bydate.columns.droplevel(0)
    ttitle = ""
    if smooth > 1:
        ttitle = f" {smooth} Day Centered Smooth Applied"
    title = (
        f"{ctx['_sname']} ({obsdf.index[0].year}-{obsdf.index[-1].year})\n"
        f"{PDICT2[varname]} Climatology {ttitle}"
    )
    # Apply sday and eday filter to both dataframes
    bydate = bydate.loc[sday:eday]
    obsdf = obsdf[(obsdf["plotdate"] >= sday) & (obsdf["plotdate"] <= eday)]

    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes((0.1, 0.55, 0.8, 0.35))
    ax.fill_between(
        bydate.index,
        bydate["min"],
        bydate["max"],
        color="tan",
        alpha=0.5,
        label="Range",
    )
    ax.fill_between(
        bydate.index,
        bydate["25%"],
        bydate["75%"],
        color="lightblue",
        alpha=0.55,
        label="25-75 Percentile",
    )
    ax.plot(bydate.index, bydate["mean"], color="k", lw=2, label="Mean")
    years = [ctx["year"], ctx.get("y2")]
    for idx, year in enumerate(years):
        if year is None:
            continue
        thisyear = obsdf.loc[f"{year}-01-01" : f"{year}-12-31"]
        if not thisyear.empty:
            style = OBS_STYLES[idx % len(OBS_STYLES)]
            ax.scatter(
                thisyear["plotdate"].values,
                thisyear[varname].values,
                label=f"{year} Obs",
                color=style["color"],
                marker=style["marker"],
                edgecolors="white",
                linewidths=0.7,
                alpha=0.95,
                zorder=6,
            )
    ax.legend(ncol=5, loc=(0.05, -0.24), fontsize=12)
    ax.grid(True)
    units = "%" if varname.find("rh") > 0 else "F"
    ax.set_ylabel(f"{PDICT2[varname]} [{units}]")
    xlabel_magic(ax, sday, eday)
    ax.set_xlim(sday - timedelta(hours=12), eday + timedelta(hours=12))

    # Frequency
    ax2 = fig.add_axes((0.1, 0.1, 0.8, 0.35))
    probs = (
        obsdf[["plotdate", "threshold_exceed"]]
        .groupby("plotdate")
        .mean()
        .rolling(window=smooth, center=True)
        .mean()
    )
    bydate["threshold_exceed_freq"] = probs["threshold_exceed"]
    ax2.plot(
        probs.index,
        probs["threshold_exceed"].values * 100.0,
        lw=2,
    )
    ax2.set_ylabel(
        f"Daily Frequency [%]\n{varname} {op} {threshold:.0f}{units}",
    )
    ax2.set_ylim(0, 100)
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax2.grid(True)
    xlabel_magic(ax2, sday, eday)
    ax2.set_xlim(sday - timedelta(hours=12), eday + timedelta(hours=12))

    return fig, bydate
