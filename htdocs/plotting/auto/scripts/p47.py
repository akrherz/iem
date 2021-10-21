"""Fall Minimum by Date"""
import calendar

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound
import seaborn as sns


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
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
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]
    year = ctx["year"]

    table = "alldata_%s" % (station[:2],)

    # beat month
    df = read_sql(
        f"""
    SELECT year, sum(precip) as precip, sum(snow) as snow from {table}
    WHERE station = %s and month = %s and precip >= 0
    and snow >= 0 GROUP by year ORDER by year ASC
    """,
        pgconn,
        params=(station, month),
        index_col="year",
    )
    if df.empty:
        raise NoDataFound("Failed to find any data for this month.")

    g = sns.jointplot(
        x="precip", y="snow", data=df, s=50, color="tan"
    ).plot_joint(sns.kdeplot, n_levels=6)
    g.fig.set_size_inches(8, 6)
    g.fig.tight_layout()
    g.fig.subplots_adjust(top=0.91)
    g.fig.suptitle(
        ("[%s] %s(%s-%s)\n%s Snowfall vs Precipitation Totals")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            df.index.min(),
            df.index.max(),
            calendar.month_name[month],
        )
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
        "%.2f" % (df["precip"].mean(),),
        va="top",
        ha="center",
        color="white",
        bbox=dict(color="black"),
    )
    xlim = g.ax_joint.get_xlim()
    g.ax_joint.text(
        xlim[1],
        df["snow"].mean(),
        "%.1f" % (df["snow"].mean(),),
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
    plotter(dict())
