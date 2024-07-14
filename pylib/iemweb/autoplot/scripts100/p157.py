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

import calendar
import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.datetime.today() - datetime.timedelta(days=1)
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
            label="Threshold [%] for Frequency",
        ),
        {
            "type": "int",
            "name": "smooth",
            "default": 7,
            "label": "Smoothing Window Size (days), 1 disables, max 60",
        },
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    threshold = ctx["thres"]
    mydir = ctx["dir"]
    varname = ctx["var"]
    smooth = ctx["smooth"]
    if smooth < 1 or smooth > 60:
        raise ValueError("Invalid smoothing window size, must be 1-60")

    op = ">=" if mydir == "above" else "<"
    with get_sqlalchemy_conn("iem") as conn:
        obsdf = pd.read_sql(
            text(f"""
            SELECT day, extract(doy from day) as doy, {varname},
            case when {varname} {op} :threshold then 1 else 0 end
            as threshold_exceed from summary s WHERE iemid = :iemid
            and {varname} is not null ORDER by day ASC
        """),
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

    thisyear = obsdf.loc[f"{year}-01-01" : f"{year}-12-31"]
    bydoy = (
        obsdf[["doy", varname]]
        .groupby("doy")
        .describe()
        .rolling(window=smooth, center=True)
        .mean()
    )
    bydoy.columns = bydoy.columns.droplevel(0)
    bydoy.index.name = "day_of_year"
    ttitle = ""
    if smooth > 1:
        ttitle = f" {smooth} Day Centered Smooth Applied"
    title = (
        f"{ctx['_sname']} ({obsdf.index[0].year}-{obsdf.index[-1].year})\n"
        f"{PDICT2[varname]} Climatology {ttitle}"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes([0.1, 0.55, 0.8, 0.35])
    ax.fill_between(
        bydoy.index.values,
        bydoy["min"],
        bydoy["max"],
        color="tan",
        label="Range",
    )
    ax.fill_between(
        bydoy.index.values,
        bydoy["25%"],
        bydoy["75%"],
        color="lightblue",
        label="25-75 Percentile",
    )
    ax.plot(bydoy.index.values, bydoy["mean"], color="k", lw=2, label="Mean")
    if not thisyear.empty:
        ax.scatter(
            thisyear["doy"].values,
            thisyear[varname].values,
            color="b",
            label=f"{year} Obs",
        )
    ax.legend(ncol=4, loc=(0.05, -0.24), fontsize=12)
    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(1, 365)
    ax.grid(True)
    units = "%" if varname.find("rh") > 0 else "F"
    ax.set_ylabel(f"{PDICT2[varname]} [{units}]")

    # Frequency
    ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.35])
    probs = (
        obsdf[["doy", "threshold_exceed"]]
        .groupby("doy")
        .mean()
        .rolling(window=smooth, center=True)
        .mean()
    )
    bydoy["threshold_exceed_freq"] = probs["threshold_exceed"]
    ax2.plot(
        probs.index.values, probs["threshold_exceed"].values * 100.0, lw=2
    )
    ax2.set_ylabel(
        f"Daily Frequency [%]\n{varname} {op} {threshold:.0f}{units}",
    )
    ax2.set_ylim(0, 100)
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax2.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax2.set_xticklabels(calendar.month_abbr[1:])
    ax2.set_xlim(1, 365)
    ax2.grid(True)
    return fig, bydoy
