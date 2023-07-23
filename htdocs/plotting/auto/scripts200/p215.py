"""
This autoplot generates some metrics on the distribution of temps
over a given period of years.  The plotted distribution in the upper panel
is using a guassian kernel density estimate.
"""
import calendar
from datetime import date, datetime

import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.plot.util import fitbox
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from scipy.stats import gaussian_kde
from sqlalchemy import text

PDICT = {
    "high": "High Temperature [F]",
    "low": "Low Temperature [F]",
    "avgt": "Average Temperature [F]",
}
MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 3600, "data": True}
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
        ts = datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        months = [ts.month]
        ctx["mlabel"] = calendar.month_name[ts.month]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                """
                SELECT high, low, (high+low)/2. as avgt from alldata WHERE
                day >= :d1 and day <= :d2 and station = :station
                and high is not null
                and low is not null and month in :months
                """
            ),
            conn,
            params={
                "d1": date(ctx[f"sy{period}"], 1, 1),
                "d2": date(ctx[f"ey{period}"], 12, 31),
                "station": ctx["station"],
                "months": tuple(months),
            },
        )
    return df


def f2s(value):
    """HAAAAAAAAAAAAACK."""
    return (f"{value:.5f}").rstrip("0").rstrip(".")


def plotter(fdict):
    """Go"""
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
    period1 = f"{ctx['sy1']}-{ctx['ey1']}"
    period2 = f"{ctx['sy2']}-{ctx['ey2']}"
    label1 = f"{period1} {ctx['v']}"
    label2 = f"{period2} {ctx['v']}"

    df = pd.DataFrame({label1: kern1(xpos), label2: kern2(xpos)}, index=xpos)

    fig = figure(apctx=ctx)
    title = (
        f"{ctx['_sname']}:: {PDICT[ctx['v']]} Distribution\n"
        f"{period2} vs {period1} over {ctx['mlabel']}"
    )
    fitbox(fig, title, 0.12, 0.9, 0.91, 0.99)

    ax = fig.add_axes([0.12, 0.38, 0.75, 0.52])
    C1 = "blue"
    C2 = "red"
    alpha = 0.4

    ax.plot(
        df.index.values,
        df[label1],
        lw=2,
        c=C1,
        label=rf"{label1}: $\mu$={df1[ctx['v']].mean():.2f}",
        zorder=4,
    )
    ax.fill_between(xpos, 0, df[label1], color=C1, alpha=alpha, zorder=3)
    ax.axvline(df1[ctx["v"]].mean(), color=C1)
    ax.plot(
        df.index.values,
        df[label2],
        lw=2,
        c=C2,
        label=rf"{label2}: $\mu$={df2[ctx['v']].mean():.2f}",
        zorder=4,
    )
    ax.fill_between(xpos, 0, df[label2], color=C2, alpha=alpha, zorder=3)
    ax.axvline(df2[ctx["v"]].mean(), color=C2)
    ax.set_ylabel("Guassian Kernel Density Estimate")
    ax.legend(loc="best")
    ax.grid(True)
    ax.xaxis.set_major_locator(MaxNLocator(20))

    # Sub ax
    ax2 = fig.add_axes([0.12, 0.1, 0.75, 0.22])
    delta = df[label2] - df[label1]
    ax2.plot(df.index.values, delta)
    dam = delta.abs().max() * 1.1
    ax2.set_ylim(0 - dam, dam)
    ax2.set_xlabel(PDICT[ctx["v"]])
    ax2.set_ylabel(f"{period2} minus\n{period1}")
    ax2.grid(True)
    ax2.fill_between(xpos, 0, delta, where=delta > 0, color=C2, alpha=alpha)
    ax2.fill_between(xpos, 0, delta, where=delta < 0, color=C1, alpha=alpha)
    ax2.axhline(0, ls="--", lw=2, color="k")
    ax2.xaxis.set_major_locator(MaxNLocator(20))

    # Percentiles
    levels = [0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75]
    levels.extend([0.9, 0.95, 0.99, 0.995, 0.999])
    p1 = df1[ctx["v"]].describe(percentiles=levels)
    p2 = df2[ctx["v"]].describe(percentiles=levels)
    y = 0.8
    fig.text(0.88, y, "Percentile", rotation=70)
    fig.text(0.91, y, period1, rotation=70)
    fig.text(0.945, y, period2, rotation=70)
    for ptile in levels:
        y -= 0.03
        val = f2s(ptile * 100.0)
        fig.text(0.88, y, val)
        v1 = p1[f"{val}%"]
        v2 = p2[f"{val}%"]
        fig.text(0.91, y, f"{v1:.1f}")
        fig.text(0.95, y, f"{v2:.1f}")

    return fig, df


if __name__ == "__main__":
    plotter({})
