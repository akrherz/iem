"""KDE of Temps."""
import calendar
from collections import OrderedDict
from datetime import date, datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.util import fitbox
from pyiem.plot.use_agg import plt
from pyiem.reference import TWITTER_RESOLUTION_INCH
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
from matplotlib.ticker import MaxNLocator
from scipy.stats import gaussian_kde
import numpy as np

PDICT = {
    "high": "High Temperature [F]",
    "low": "Low Temperature [F]",
    "avgt": "Average Temperature [F]",
}
MDICT = OrderedDict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 3600
    desc["data"] = True
    desc[
        "description"
    ] = """This autoplot generates some metrics on the distribution of temps
    over a given period of years.  The plotted distribution in the upper panel
    is using a guassian kernel density estimate.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=PDICT,
            name="v",
            default="high",
            label="Daily Variable to Plot:",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="year",
            min=1880,
            name="sy1",
            default=1981,
            label="Inclusive Start Year for First Period of Years:",
        ),
        dict(
            type="year",
            min=1880,
            name="ey1",
            default=2010,
            label="Inclusive End Year for First Period of Years:",
        ),
        dict(
            type="year",
            min=1880,
            name="sy2",
            default=1991,
            label="Inclusive Start Year for Second Period of Years:",
        ),
        dict(
            type="year",
            min=1880,
            name="ey2",
            default=2020,
            label="Inclusive End Year for Second Period of Years:",
        ),
    ]
    return desc


def get_df(ctx, period):
    """Get our data."""
    pgconn = get_dbconn("coop")
    table = "alldata_%s" % (ctx["station"][:2])
    month = ctx["month"]
    ctx["mlabel"] = f"{month.capitalize()} Season"
    if month == "all":
        months = range(1, 13)
        ctx["mlabel"] = "All Year"
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        months = [ts.month]
        ctx["mlabel"] = calendar.month_name[ts.month]

    return read_sql(
        f"SELECT high, low, (high+low)/2. as avgt from {table} WHERE "
        "day >= %s and day <= %s and station = %s and high is not null "
        "and low is not null and month in %s",
        pgconn,
        params=(
            date(ctx[f"sy{period}"], 1, 1),
            date(ctx[f"ey{period}"], 12, 31),
            ctx["station"],
            tuple(months),
        ),
    )


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    df1 = get_df(ctx, "1")
    df2 = get_df(ctx, "2")
    if df1.empty or df2.empty:
        raise NoDataFound("Failed to find data for query!")
    kern1 = gaussian_kde(df1[ctx["v"]])
    kern2 = gaussian_kde(df2[ctx["v"]])

    xpos = np.arange(
        min([df1[ctx["v"]].min(), df2[ctx["v"]].min()]),
        max([df1[ctx["v"]].max(), df2[ctx["v"]].max()]) + 1,
        dtype="i",
    )
    period1 = "%s-%s" % (ctx["sy1"], ctx["ey1"])
    period2 = "%s-%s" % (ctx["sy2"], ctx["ey2"])
    label1 = "%s-%s %s" % (ctx["sy1"], ctx["ey1"], ctx["v"])
    label2 = "%s-%s %s" % (ctx["sy2"], ctx["ey2"], ctx["v"])

    df = pd.DataFrame({label1: kern1(xpos), label2: kern2(xpos)}, index=xpos)

    fig = plt.figure(figsize=TWITTER_RESOLUTION_INCH)
    title = "[%s] %s %s Distribution\n%s vs %s over %s" % (
        ctx["station"],
        ctx["_nt"].sts[ctx["station"]]["name"],
        PDICT[ctx["v"]],
        period2,
        period1,
        ctx["mlabel"],
    )
    fitbox(fig, title, 0.12, 0.9, 0.91, 0.99)

    ax = fig.add_axes([0.12, 0.38, 0.75, 0.52])
    C1 = "blue"
    C2 = "red"
    alpha = 0.4

    ax.plot(df.index.values, df[label1], lw=2, c=C1, label=label1, zorder=4)
    ax.fill_between(xpos, 0, df[label1], color=C1, alpha=alpha, zorder=3)
    ax.plot(df.index.values, df[label2], lw=2, c=C2, label=label2, zorder=4)
    ax.fill_between(xpos, 0, df[label2], color=C2, alpha=alpha, zorder=3)
    ax.set_ylabel("Guassian Kernel Density Estimate")
    ax.legend(loc=2)
    ax.grid(True)
    ax.xaxis.set_major_locator(MaxNLocator(20))

    # Sub ax
    ax2 = fig.add_axes([0.12, 0.1, 0.75, 0.22])
    delta = df[label2] - df[label1]
    ax2.plot(df.index.values, delta)
    dam = delta.abs().max() * 1.1
    ax2.set_ylim(0 - dam, dam)
    ax2.set_xlabel(PDICT[ctx["v"]])
    ax2.set_ylabel("%s minus\n%s" % (period2, period1))
    ax2.grid(True)
    ax2.fill_between(xpos, 0, delta, where=delta > 0, color=C2, alpha=alpha)
    ax2.fill_between(xpos, 0, delta, where=delta < 0, color=C1, alpha=alpha)
    ax2.axhline(0, ls="--", lw=2, color="k")
    ax2.xaxis.set_major_locator(MaxNLocator(20))

    # Percentiles
    p1 = df1[ctx["v"]].describe(percentiles=np.arange(0, 1.01, 0.01))
    p2 = df2[ctx["v"]].describe(percentiles=np.arange(0, 1.01, 0.01))
    y = 0.8
    fig.text(0.88, y, "Percentile", rotation=45)
    fig.text(0.91, y, period1, rotation=45)
    fig.text(0.94, y, period2, rotation=45)
    for ptile in [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]:
        y -= 0.03
        fig.text(0.88, y, str(int(ptile * 100.0)))
        fig.text(0.9, y, "%.1f" % (p1[f"{int(ptile * 100.)}%"],))
        fig.text(0.94, y, "%.1f" % (p2[f"{int(ptile * 100.)}%"],))

    return fig, df


if __name__ == "__main__":
    plotter(dict())
