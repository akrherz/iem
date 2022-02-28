"""Fall Minimum by Date"""
import calendar

import pandas as pd
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.reference import FIGSIZES
from pyiem.exceptions import NoDataFound
import seaborn as sns


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["defaults"] = {"_r": "86"}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart displays the combination of liquid
    precipitation with snowfall totals for a given month.  The liquid totals
    include the melted snow.  So this plot does <strong>not</strong> show
    the combination of non-frozen vs frozen precipitation. For a given winter
    month, not all precipitation falls as snow, so you can not assume that
    the liquid equivalent did not include some liquid rainfall."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(type="month", name="month", default="12", label="Select Month:"),
        dict(
            type="year",
            name="year",
            default="2014",
            label="Select Year to Highlight:",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    year = ctx["year"]

    with get_sqlalchemy_conn("coop") as conn:
        # beat month
        df = pd.read_sql(
            f"""
        SELECT year, sum(precip) as precip, sum(snow) as snow from
        alldata_{station[:2]}
        WHERE station = %s and month = %s and precip >= 0
        and snow >= 0 GROUP by year ORDER by year ASC
        """,
            conn,
            params=(station, month),
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("Failed to find any data for this month.")

    g = sns.jointplot(
        x="precip", y="snow", data=df, s=50, color="tan"
    ).plot_joint(sns.kdeplot, n_levels=6)
    g.fig.set_size_inches(*FIGSIZES[ctx["_r"]])
    g.fig.tight_layout()
    g.fig.subplots_adjust(top=0.91)
    g.fig.suptitle(
        f"[{station}] {ctx['_nt'].sts[station]['name']}"
        f"({df.index.min()}-{df.index.max()})\n"
        f"{calendar.month_name[month]} Snowfall vs Precipitation Totals"
    )
    if year in df.index:
        row = df.loc[year]
        g.ax_joint.scatter(
            row["precip"],
            row["snow"],
            s=60,
            marker="o",
            color="r",
            zorder=3,
            label=str(year),
        )
    g.ax_joint.grid(True)
    g.ax_joint.axhline(df["snow"].mean(), lw=2, color="black")
    g.ax_joint.axvline(df["precip"].mean(), lw=2, color="black")

    g.ax_joint.set_xlim(left=-0.1)
    g.ax_joint.set_ylim(bottom=-0.3)
    ylim = g.ax_joint.get_ylim()
    g.ax_joint.text(
        df["precip"].mean(),
        ylim[1],
        f"{df['precip'].mean():.2f}",
        va="top",
        ha="center",
        color="white",
        bbox=dict(color="black"),
    )
    xlim = g.ax_joint.get_xlim()
    g.ax_joint.text(
        xlim[1],
        df["snow"].mean(),
        f"{df['snow'].mean():.1f}",
        va="center",
        ha="right",
        color="white",
        bbox=dict(color="black"),
    )
    g.ax_joint.set_ylabel("Snowfall Total [inch]")
    g.ax_joint.set_xlabel("Precipitation Total (liquid + melted) [inch]")
    g.ax_joint.legend(loc=1, scatterpoints=1)
    return g.fig, df


if __name__ == "__main__":
    plotter({})
