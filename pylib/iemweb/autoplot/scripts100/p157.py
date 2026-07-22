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
from matplotlib import dates as mdates
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


DOY_ORIGIN = datetime(2000, 1, 1)
OBS_STYLES = (
    {"color": "#111111", "marker": "o"},
    {"color": "#8B1E3F", "marker": "D"},
)


def _doy_to_date(doy):
    """Convert 1-366 day-of-year values into a leap-year datetime axis."""
    return pd.to_datetime(doy - 1, unit="D", origin=DOY_ORIGIN)


def _apply_doy_axis(ax: Axes, start_doy: int, end_doy: int) -> None:
    """Use matplotlib's built-in auto date locator and concise labels."""
    locator = mdates.AutoDateLocator(minticks=4, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ["", "%b", "%-d", "%H:%M", "%H:%M", "%S.%f"]
    formatter.zero_formats = [
        "",
        "%b",
        "%b %-d",
        "%H:%M",
        "%H:%M",
        "%S.%f",
    ]
    formatter.offset_formats = ["", "", "", "", "", ""]
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlim(
        _doy_to_date(start_doy) - timedelta(hours=12),
        _doy_to_date(end_doy) + timedelta(hours=12),
    )


def _apply_visible_ylim(
    ax: Axes,
    bydoy: pd.DataFrame,
    obsdf: pd.DataFrame,
    varname: str,
    years: list,
    start_doy: int,
    end_doy: int,
) -> None:
    """Scale y-limits to data visible in the selected day-of-year window."""
    low_doy = min(start_doy, end_doy)
    high_doy = max(start_doy, end_doy)
    window = bydoy.loc[low_doy:high_doy]
    yvals = [window["min"], window["max"], window["mean"]]

    for year in years:
        if year is None:
            continue
        thisyear = obsdf.loc[f"{year}-01-01" : f"{year}-12-31"]
        if thisyear.empty:
            continue
        yvals.append(
            thisyear[
                (thisyear["doy"] >= low_doy) & (thisyear["doy"] <= high_doy)
            ][varname]
        )

    valid = pd.concat(yvals).dropna()
    if valid.empty:
        return

    ymin = valid.min()
    ymax = valid.max()
    if ymin == ymax:
        pad = max(1.0, abs(ymin) * 0.05)
    else:
        pad = (ymax - ymin) * 0.05
    ax.set_ylim(ymin - pad, ymax + pad)


def _obs_marker_size(start_doy: int, end_doy: int) -> float:
    """Increase marker size for short windows, keep long windows unchanged."""
    span = max(1, abs(end_doy - start_doy) + 1)
    if span >= 180:
        return 28.0
    # Linearly ramp up from 28 at 180 days to 62 at 1 day.
    return min(62.0, 28.0 + (180 - span) * (34.0 / 179.0))


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
            label="Threshold [%] for Frequency",
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
    if smooth < 1 or smooth > 60:
        raise ValueError("Invalid smoothing window size, must be 1-60")

    op = ">=" if mydir == "above" else "<"
    with get_sqlalchemy_conn("iem") as conn:
        obsdf = pd.read_sql(
            sql_helper(
                """
            SELECT day, extract(doy from day) as doy, {varname},
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
    start_doy = int(f"{ctx['sday']:%j}")
    end_doy = int(f"{ctx['eday']:%j}")
    marker_size = _obs_marker_size(start_doy, end_doy)
    fig = figure(apctx=ctx, title=title)
    ax = fig.add_axes((0.1, 0.55, 0.8, 0.35))
    bydoy_dates = _doy_to_date(bydoy.index.values)
    ax.fill_between(
        bydoy_dates,
        bydoy["min"],
        bydoy["max"],
        color="tan",
        alpha=0.5,
        label="Range",
    )
    ax.fill_between(
        bydoy_dates,
        bydoy["25%"],
        bydoy["75%"],
        color="lightblue",
        alpha=0.55,
        label="25-75 Percentile",
    )
    ax.plot(bydoy_dates, bydoy["mean"], color="k", lw=2, label="Mean")
    years = [ctx["year"], ctx.get("y2")]
    for idx, year in enumerate(years):
        if year is None:
            continue
        thisyear = obsdf.loc[f"{year}-01-01" : f"{year}-12-31"]
        if not thisyear.empty:
            style = OBS_STYLES[idx % len(OBS_STYLES)]
            ax.scatter(
                _doy_to_date(thisyear["doy"].values),
                thisyear[varname].values,
                label=f"{year} Obs",
                color=style["color"],
                marker=style["marker"],
                edgecolors="white",
                linewidths=0.7,
                s=marker_size,
                alpha=0.95,
                zorder=6,
            )
    ax.legend(ncol=5, loc=(0.05, -0.24), fontsize=12)
    _apply_doy_axis(ax, start_doy, end_doy)
    _apply_visible_ylim(ax, bydoy, obsdf, varname, years, start_doy, end_doy)
    ax.grid(True)
    units = "%" if varname.find("rh") > 0 else "F"
    ax.set_ylabel(f"{PDICT2[varname]} [{units}]")

    # Frequency
    ax2 = fig.add_axes((0.1, 0.1, 0.8, 0.35))
    probs = (
        obsdf[["doy", "threshold_exceed"]]
        .groupby("doy")
        .mean()
        .rolling(window=smooth, center=True)
        .mean()
    )
    bydoy["threshold_exceed_freq"] = probs["threshold_exceed"]
    ax2.plot(
        _doy_to_date(probs.index.values),
        probs["threshold_exceed"].values * 100.0,
        lw=2,
    )
    ax2.set_ylabel(
        f"Daily Frequency [%]\n{varname} {op} {threshold:.0f}{units}",
    )
    ax2.set_ylim(0, 100)
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    _apply_doy_axis(ax2, start_doy, end_doy)
    ax2.grid(True)
    return fig, bydoy
