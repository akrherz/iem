"""Fall Minimum by Date"""
import calendar

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
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
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    year = ctx["year"]

    table = "alldata_%s" % (station[:2],)

    # beat month
    df = read_sql(
        """
    SELECT year, sum(precip) as precip, sum(snow) as snow from """
        + table
        + """
    WHERE station = %s and month = %s and precip >= 0
    and snow >= 0 GROUP by year ORDER by year ASC
    """,
        pgconn,
        params=(station, month),
        index_col="year",
    )

    (fig, ax) = plt.subplots(1, 1)

    ax.scatter(df["precip"], df["snow"], s=40, marker="s", color="b", zorder=2)
    if year in df.index:
        row = df.loc[year]
        ax.scatter(
            row["precip"],
            row["snow"],
            s=60,
            marker="o",
            color="r",
            zorder=3,
            label=str(year),
        )
    ax.set_title(
        ("[%s] %s\n%s Snowfall vs Precipitation Totals")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            calendar.month_name[month],
        )
    )
    ax.grid(True)
    ax.axhline(df["snow"].mean(), lw=2, color="black")
    ax.axvline(df["precip"].mean(), lw=2, color="black")

    ax.set_xlim(left=-0.1)
    ax.set_ylim(bottom=-0.1)
    ylim = ax.get_ylim()
    ax.text(
        df["precip"].mean(),
        ylim[1],
        "%.2f" % (df["precip"].mean(),),
        va="top",
        ha="center",
        color="white",
        bbox=dict(color="black"),
    )
    xlim = ax.get_xlim()
    ax.text(
        xlim[1],
        df["snow"].mean(),
        "%.1f" % (df["snow"].mean(),),
        va="center",
        ha="right",
        color="white",
        bbox=dict(color="black"),
    )
    ax.set_ylabel("Snowfall Total [inch]")
    ax.set_xlabel("Precipitation Total (liquid + melted) [inch]")
    ax.legend(loc=2, scatterpoints=1)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
