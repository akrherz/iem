"""
This plot compares the distribution of daily
temperatures for two months or periods for a single station of your choice.
The left hand plot depicts a quantile - quantile plot, which simply plots
the montly percentile values against each other.  You could think of this
plot as comparable frequencies.  The right hand plot depicts the
distribution of each month's temperatures expressed as a violin plot. These
type of plots are useful to see the shape of the distribution.  These plots
also contain the mean and extremes of the distributions.

<br />There is an additional bit of functionality allowing for the
computation of metrics over a number of trailing days.  When this
trailing day window period is set to a value larger than 1 day, you will
want to also set the computation method over that window.  The options
are:
<ul>
    <li>Max: Take the day with the highest value</li>
    <li>Avg: Take the average of all days in the window</li>
    <li>Min: Take the lowest value over the window</li>
</ul>
<br />Clever combinations of the above allow for assessment of strength
and duration of stretches of hot or cold weather.
"""

import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context
from scipy import stats

ODICT = {"max": "Maximum", "min": "Minimum", "avg": "Average"}
PDICT = {
    "high": "Daily High Temperature",
    "low": "Daily Low Temperature",
    "avg": "Daily Average Temperature",
}
MDICT = {
    "year": "Calendar Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": True, "description": __doc__}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            network="IACLIMATE",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="month1",
            default="12",
            options=MDICT,
            label="Select Month for x-axis:",
        ),
        dict(
            type="text",
            default="1893-1950",
            name="p1",
            optional=True,
            label="Inclusive Period of Years for x-axis (Optional)",
        ),
        dict(
            type="select",
            name="month2",
            default="7",
            options=MDICT,
            label="Select Month for y-axis:",
        ),
        dict(
            type="text",
            default="1950-2017",
            name="p2",
            optional=True,
            label="Inclusive Period of Years for y-axis (Optional)",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            label="Variable to Compare",
            options=PDICT,
        ),
        dict(
            type="float",
            label="x-axis Value to Highlight",
            default=55,
            name="highlight",
        ),
        dict(
            type="int",
            default="1",
            name="days",
            label="Evaluate over X number of days",
        ),
        dict(
            type="select",
            name="opt",
            options=ODICT,
            default="max",
            label="When evaluation over multiple days, how to compute:",
        ),
    ]
    return desc


def get_data(station, month, period, varname, days, opt):
    """Get Data please"""
    doffset = "0 days"
    if len(month) < 3:
        mlimiter = f" and month = {int(month)} "
    elif month == "all":
        mlimiter = ""
    elif month == "fall":
        mlimiter = " and month in (9, 10, 11) "
    elif month == "winter":
        mlimiter = " and month in (12, 1, 2) "
        doffset = "31 days"
    elif month == "spring":
        mlimiter = " and month in (3, 4, 5) "
    else:  # summer
        mlimiter = " and month in (6, 7, 8) "

    ylimiter = ""
    if period is not None:
        (y1, y2) = [int(x) for x in period.split("-")]
        ylimiter = f"WHERE myyear >= {y1} and myyear <= {y2}"
    if days == 1:
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                f"""
            WITH data as (
                SELECT
                extract(year from day + '{doffset}'::interval)::int
                as myyear,
                high, low, (high+low)/2. as avg from alldata
                WHERE station = %s and high is not null
                and low is not null {mlimiter})
            SELECT * from data {ylimiter}
            """,
                conn,
                params=(station,),
                index_col=None,
            )
    else:
        res = (
            f"{opt}({varname}) OVER (ORDER by day ASC ROWS "
            f"BETWEEN {days - 1} PRECEDING AND CURRENT ROW) "
        )
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                f"""
            WITH data as (
                SELECT
                extract(year from day + '{doffset}'::interval)::int
                as myyear,
                high, low, (high+low)/2. as avg, day, month from alldata
                WHERE station = %s and high is not null and low is not null),
            agg1 as (
                SELECT myyear, month, {res} as {varname}
                from data WHERE 1 = 1 {mlimiter})
            SELECT * from agg1 {ylimiter}
            """,
                conn,
                params=(station,),
                index_col=None,
            )
    if df.empty:
        raise NoDataFound("No Data Found.")
    mdata = df[varname].values
    if period is None:
        y1 = df["myyear"].min()
        y2 = df["myyear"].max()
    return mdata, y1, y2


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month1 = ctx["month1"]
    month2 = ctx["month2"]
    highlight = ctx["highlight"]
    varname = ctx["var"]
    p1 = ctx.get("p1")
    p2 = ctx.get("p2")
    days = ctx["days"]
    opt = ctx["opt"]

    m1data, y1, y2 = get_data(station, month1, p1, varname, days, opt)
    m2data, y3, y4 = get_data(station, month2, p2, varname, days, opt)

    pc1 = np.percentile(m1data, range(0, 101, 1))
    pc2 = np.percentile(m2data, range(0, 101, 1))
    df = pd.DataFrame(
        {
            f"{MDICT[month1]}_{varname}_{y1}_{y2}": pd.Series(pc1),
            f"{MDICT[month2]}_{varname}_{y3}_{y4}": pd.Series(pc2),
            "quantile": pd.Series(range(0, 101, 5)),
        }
    )
    s_slp, s_int, s_r, _, _ = stats.linregress(pc1, pc2)

    fig = figure(apctx=ctx)
    ax = fig.add_axes([0.1, 0.11, 0.4, 0.76])
    ax.scatter(pc1[::5], pc2[::5], s=40, marker="s", color="b", zorder=3)
    ax.plot(
        pc1,
        pc1 * s_slp + s_int,
        lw=3,
        color="r",
        zorder=2,
        label=r"Fit R$^2$=" f"{s_r**2:.2f}",
    )
    ax.axvline(highlight, zorder=1, color="k")
    y = highlight * s_slp + s_int
    ax.axhline(y, zorder=1, color="k")
    ax.text(
        pc1[0],
        y,
        f"{y:.0f}" r" $^\circ$F",
        va="center",
        bbox=dict(color="white"),
    )
    ax.text(
        highlight,
        pc2[0],
        f"{highlight:.0f}" r" $^\circ$F",
        ha="center",
        rotation=90,
        bbox=dict(color="white"),
    )
    t2 = PDICT[varname]
    if days > 1:
        t2 = f"{ODICT[opt]} {PDICT[varname]} over {days} days"
    fig.suptitle(
        f"{ctx['_sname']}\n"
        f"{MDICT[month2]} ({y1}-{y2}) vs {MDICT[month1]} ({y3}-{y4})\n{t2}"
    )
    ax.set_xlabel(
        f"{MDICT[month1]} ({y1}-{y2}) {PDICT[varname]}" r" $^\circ$F"
    )
    ax.set_ylabel(
        f"{MDICT[month2]} ({y3}-{y4}) {PDICT[varname]}" r" $^\circ$F"
    )
    ax.text(
        0.5,
        1.01,
        "Quantile - Quantile Plot",
        transform=ax.transAxes,
        ha="center",
    )
    ax.grid(True)
    ax.legend(loc=2)

    # Second
    ax = fig.add_axes([0.56, 0.18, 0.26, 0.68])
    ax.set_title("Distribution")
    v1 = ax.violinplot(m1data, positions=[0], showextrema=True, showmeans=True)
    b = v1["bodies"][0]
    m = np.mean(b.get_paths()[0].vertices[:, 0])
    b.get_paths()[0].vertices[:, 0] = np.clip(
        b.get_paths()[0].vertices[:, 0], -np.inf, m
    )
    b.set_color("r")
    for lbl in ["cmins", "cmeans", "cmaxes"]:
        v1[lbl].set_color("r")

    v1 = ax.violinplot(m2data, positions=[0], showextrema=True, showmeans=True)
    b = v1["bodies"][0]
    m = np.mean(b.get_paths()[0].vertices[:, 0])
    b.get_paths()[0].vertices[:, 0] = np.clip(
        b.get_paths()[0].vertices[:, 0], m, np.inf
    )
    b.set_color("b")
    for lbl in ["cmins", "cmeans", "cmaxes"]:
        v1[lbl].set_color("b")

    pr0 = plt.Rectangle((0, 0), 1, 1, fc="r")
    pr1 = plt.Rectangle((0, 0), 1, 1, fc="b")
    ax.legend(
        (pr0, pr1),
        (
            f"{MDICT[month1]} ({y1}-{y2}),"
            r" $\mu$"
            f"={np.mean(m1data):.1f}",
            f"{MDICT[month2]} ({y3}-{y4}),"
            r" $\mu$"
            f"={np.mean(m2data):.1f}",
        ),
        ncol=1,
        loc=(0.1, -0.2),
    )
    ax.set_ylabel(f"{PDICT[varname]}" r" $^\circ$F")
    ax.grid()

    # Third
    monofont = FontProperties(family="monospace")
    y = 0.86
    x = 0.83
    col1 = f"{MDICT[month1]}_{varname}_{y1}_{y2}"
    col2 = f"{MDICT[month2]}_{varname}_{y3}_{y4}"
    fig.text(x, y + 0.04, "Percentile Data    Diff")
    for percentile in [
        100,
        99,
        98,
        97,
        96,
        95,
        92,
        90,
        75,
        50,
        25,
        10,
        8,
        5,
        4,
        3,
        2,
        1,
    ]:
        row = df.loc[percentile]
        fig.text(x, y, f"{percentile:3.0f}", fontproperties=monofont)
        fig.text(
            x + 0.025,
            y,
            f"{row[col1]:5.1f}",
            fontproperties=monofont,
            color="r",
        )
        fig.text(
            x + 0.07,
            y,
            f"{row[col2]:5.1f}",
            fontproperties=monofont,
            color="b",
        )
        fig.text(
            x + 0.11,
            y,
            f"{(row[col2] - row[col1]):5.1f}",
            fontproperties=monofont,
        )
        y -= 0.04

    return fig, df


if __name__ == "__main__":
    plotter({})
