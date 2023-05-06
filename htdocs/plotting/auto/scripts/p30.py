"""monthly or yearly temperature range"""
import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {"monthly": "Plot Single Month", "yearly": "Plot Entire Year"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["defaults"] = {"_r": "96"}
    desc[
        "description"
    ] = """This chart presents the range between the warmest
    high temperature and the coldest low temperature for a given month for
    each year.  The bottom panel displays the range between those two values.
    The black lines represent the simple averages of the data.
    """
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="opt",
            default="monthly",
            options=PDICT,
            label="Plot a Single Month or Entire Year?",
        ),
        dict(
            type="month",
            name="month",
            default=today.month,
            label="Month to Plot:",
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year to Highlight:",
        ),
        dict(
            type="year",
            name="eyear",
            default=today.year,
            label="Last Year to Plot (inclusive):",
        ),
    ]
    return desc


def plot_trailing(ax, df, colname):
    """Plot some things"""
    trail = []
    vals = df[colname].values
    for i in range(30, len(vals)):
        trail.append(np.mean(vals[i - 30 : i]))
    ax.plot(df.index.values[30:], trail, lw=4, color="yellow", zorder=4)
    ax.plot(
        df.index.values[30:],
        trail,
        lw=1.5,
        color="red",
        zorder=5,
        label="Trailing 30yr",
    )
    ax.axhline(df[colname].mean(), lw=2, color="k", zorder=2, label="Avg")
    ax.text(
        df.index.values[-1] + 2,
        df[colname].mean(),
        f"{df[colname].mean():.0f}",
        ha="left",
        va="center",
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    year = ctx["year"]

    if ctx["opt"] == "monthly":
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                """
            SELECT year,  max(high) as max_high,  min(low) as min_low
            from alldata where station = %s and month = %s and
            high is not null and low is not null
            and year <= %s GROUP by year
            ORDER by year ASC
            """,
                conn,
                params=(station, month, ctx["eyear"]),
                index_col="year",
            )
    else:
        with get_sqlalchemy_conn("coop") as conn:
            df = pd.read_sql(
                """
            SELECT year,  max(high) as max_high,  min(low) as min_low
            from alldata where station = %s and
            high is not null and low is not null
            and year <= %s GROUP by year
            ORDER by year ASC
            """,
                conn,
                params=(station, ctx["eyear"]),
                index_col="year",
            )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["rng"] = df["max_high"] - df["min_low"]

    tt = calendar.month_name[month] if ctx["opt"] == "monthly" else "Yearly"
    title = f"{ctx['_sname']}\n" f"{tt} Temperature Range (Max High - Min Low)"
    fig = figure(title=title, apctx=ctx)
    ax = fig.subplots(3, 1, sharex=True)
    ax[0].scatter(df.index.values, df["max_high"].values)
    if year in df.index:
        ax[0].scatter(
            year, df.at[year, "max_high"], marker="o", color="r", s=10
        )
    plot_trailing(ax[0], df, "max_high")
    ax[0].grid(True)
    ax[0].set_ylabel(r"Max Temp $^\circ$F")
    ax[0].set_xlim(df.index.min() - 1.5, df.index.max() + 1.5)
    ax[0].legend(ncol=2, loc=(0.0, -0.2))

    ax[1].scatter(df.index.values, df["min_low"])
    if year in df.index:
        ax[1].scatter(
            year, df.at[year, "min_low"], marker="o", color="r", s=10
        )
    plot_trailing(ax[1], df, "min_low")
    ax[1].grid(True)
    ax[1].set_ylabel(r"Min Temp $^\circ$F")

    ax[2].scatter(df.index.values, df["rng"], zorder=1)
    plot_trailing(ax[2], df, "rng")
    if year in df.index:
        ax[2].scatter(year, df.at[year, "rng"], marker="o", color="r", s=10)
        ax[2].set_title(
            f"Year {year} [Hi: {df.at[year, 'max_high']} "
            f"Lo: {df.at[year, 'min_low']} Rng: {df.at[year, 'rng']}] "
            "Highlighted",
            color="r",
        )
    ax[2].set_ylabel(r"Temperature Range $^\circ$F")
    ax[2].grid(True)

    return fig, df


if __name__ == "__main__":
    plotter({})
