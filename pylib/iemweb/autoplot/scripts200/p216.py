"""
This chart presents the longest daily streaks of having some
threshold meet.  This tool presents a number of variables that may not be
observed by your station or network.  If you pick a below threshold, then the
year is split on 1 July and the year plotted is the year of the second half of
that period. <a href="/request/daily.phtml">Daily Data Request Form</a>
provides the raw values for the automated stations.  The download portal for
the long term climate sites is <a href="/request/coop/fe.phtml">here</a>.
"""

import datetime

import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import get_monofont

PDICT = {
    "above": "At or Above (AOA) Threshold",
    "below": "Below Threshold",
}
PDICT2 = {
    "high": "Daily High Temperature",
    "low": "Daily Low Temperature",
    "max_dwpf": "Daily Max Dew Point",
    "min_dwpf": "Daily Min Dew Point",
    "max_feel": "Daily Max Feels Like Temp",
    "min_feel": "Daily Min Feels Like Temp",
    "max_sknt": "Daily Max Sustained Wind Speed",
    "max_gust": "Daily Max Wind Gust",
}
UNITS = {
    "high": "F",
    "low": "F",
    "max_dwpf": "F",
    "min_dwpf": "F",
    "max_feel": "F",
    "min_feel": "F",
    "max_sknt": "kts",
    "max_gust": "kts",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        {
            "type": "sid",
            "name": "station",
            "default": "IATDSM",
            "label": "Select Station:",
            "network": "IACLIMATE",
            "include_climodat": True,
        },
        dict(
            type="select",
            name="var",
            default="high",
            options=PDICT2,
            label="Select which daily variable",
        ),
        dict(
            type="select",
            name="dir",
            default="below",
            options=PDICT,
            label="Select temperature direction",
        ),
        dict(
            type="int",
            name="threshold",
            default="32",
            label="hreshold (F or knots):",
        ),
    ]
    return desc


def get_data(ctx):
    """Get the data for this plot."""
    varname = ctx["var"]
    station = ctx["station"]
    if ctx["network"].find("CLIMATE") > 0:
        with get_sqlalchemy_conn("coop") as conn:
            obsdf = pd.read_sql(
                text(f"""
                select day, {varname},
                case when month > 6 then year + 1 else year end as season
                from alldata where station = :station and {varname} is not null
                ORDER by day ASC
            """),
                conn,
                params={"station": station},
                parse_dates="day",
                index_col="day",
            )
    else:
        varname = {"high": "max_tmpf", "low": "min_tmpf"}.get(varname, varname)
        with get_sqlalchemy_conn("iem") as conn:
            obsdf = pd.read_sql(
                text(f"""
                select day, {varname},
                case when extract(month from day) > 6 then
                    extract(year from day) + 1 else extract(year from day)
                    end as season
                from summary where iemid = :iemid and {varname} is not null
                ORDER by day ASC
            """),
                conn,
                params={"iemid": ctx["_nt"].sts[station]["iemid"]},
                parse_dates="day",
                index_col="day",
            )
    return obsdf


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    threshold = ctx["threshold"]
    varname = ctx["var"]
    mydir = ctx["dir"]

    op = np.greater_equal if mydir == "above" else np.less
    rows = []
    startdate = None
    running = 0
    row = None
    obsdf = get_data(ctx)
    if obsdf.empty:
        raise NoDataFound("Did not find any observations for station.")
    obsdf = obsdf.reindex(pd.date_range(obsdf.index.min(), obsdf.index.max()))
    for day, row in obsdf.iterrows():
        if op(row[varname], threshold):
            if running == 0:
                startdate = day
            running += 1
            continue
        if running == 0:
            continue
        rows.append(
            {
                "days": running,
                "season": day.year if mydir == "above" else row["season"],
                "startdate": startdate,
                "enddate": day - datetime.timedelta(days=1),
            }
        )
        running = 0
    if running > 0:
        rows.append(
            {
                "days": running,
                "season": day.year if mydir == "above" else row["season"],
                "startdate": startdate,
                "enddate": day,
            }
        )
    if not rows:
        raise NoDataFound("Failed to find any streaks for given threshold.")
    df = pd.DataFrame(rows)

    label = "at or above" if mydir == "above" else "below"
    label2 = "Yearly" if mydir == "above" else "Seasonal"
    title = (
        f"{ctx['_sname']} "
        f"[{obsdf.index[0]:%-d %b %Y}-{obsdf.index[-1]:%-d %b %Y}]:: "
        f"{label2} Maximum Consecutive Days with"
    )
    subtitle = f"{PDICT2[varname]} {label} {threshold} {UNITS[varname]}"
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.5, 0.8])
    ax.set_ylabel(f"Max Streak by {label2} [days]")
    ax.grid(True)
    gdf = df.groupby("season").max()
    ax.bar(gdf.index.values, gdf["days"].values, width=1)
    val = gdf["days"].mean()
    ax.axhline(val, lw=2, color="r")
    ax.text(
        gdf.index.values[-1] + 2,
        val,
        f"Avg: {val:.1f}",
        color="r",
        bbox=dict(color="white"),
    )
    ax.set_xlabel(label2)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    # List out longest
    monofont = get_monofont()
    monofont.set_size(14)
    y = 0.84
    fig.text(
        0.65,
        y,
        "Top 20 Events\nStart Date  End Date     Days",
        fontproperties=monofont,
    )
    y -= 0.045
    fmt = "%b %-2d %Y"
    for _, row in (
        df.sort_values(by="days", ascending=False).head(20).iterrows()
    ):
        fig.text(
            0.65,
            y,
            "%s %s  %3i"
            % (
                row["startdate"].strftime(fmt),
                row["enddate"].strftime(fmt),
                row["days"],
            ),
            fontproperties=monofont,
        )
        y -= 0.034

    return fig, df
