"""
This plot shows the number of days with a high
temperature at or above a given threshold.  You can optionally generate
this plot for the year to date period.  The present year is not used for
the computation of the average nor minimum value.
"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

PDICT = {
    "full": "Show Full Year Totals",
    "ytd": "Limit to Year to Date Period",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="year",
            name="year",
            default=today.year,
            label="Year to Compare:",
        ),
        dict(
            type="select",
            options=PDICT,
            default="full",
            label="Day Period Limit:",
            name="limit",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    limit = ctx["limit"]
    limitsql = ""
    limittitle = ""
    today = datetime.date.today() - datetime.timedelta(days=1)
    params = {"station": station}
    if limit == "ytd":
        limittitle = f"(Jan 1 - {today:%b %-d})"
        params["doy"] = int(today.strftime("%j"))
        limitsql = " and extract(doy from day) <= :doy "

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound(f"{station} has no archive_begin")
    params["sts"] = ab.strftime("%Y-%m-%d")
    if ab.strftime("%m%d") != "0101":
        # Truncate up to the next year
        params["sts"] = f"{ab.year + 1}-01-01"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                "SELECT year, day, high from alldata WHERE "
                "station = :station and day >= :sts and "
                f"high is not null {limitsql} ORDER by day ASC"
            ),
            conn,
            params=params,
            index_col="day",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    res = []
    maxval2 = int(df["high"].max())
    years = df["year"].unique()
    for level in range(maxval2 - 30, maxval2 + 2):
        gdf = (
            df[df["high"] >= level]
            .groupby("year")
            .count()
            .reindex(years)
            .fillna(0)
        )
        maxval = gdf.max()["high"]
        if maxval == 0:
            continue
        label = ",".join(
            [str(s) for s in list(gdf[gdf["high"] == maxval].index.values)]
        )
        thisyear = 0
        if year in gdf.index.values:
            thisyear = gdf.at[year, "high"]
        res.append(
            dict(
                avgval=gdf.iloc[:-1].mean()["high"],
                minval=gdf.iloc[:-1].min()["high"],
                level=level,
                label=label,
                max=maxval,
                thisyear=thisyear,
            )
        )

    df = pd.DataFrame(res)
    df = df.set_index("level")

    title = (
        f"{ctx['_sname']} :: Max Days per Year {limittitle}\n"
        "at or above given high temperature threshold"
    )

    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.barh(df.index.values, df["max"].values, label="Max", zorder=2)
    ax.barh(df.index.values, df["thisyear"].values, label=f"{year}", zorder=3)
    ax.scatter(
        df["minval"].values,
        df.index.values,
        label="Min",
        marker="^",
        zorder=4,
        color="black",
    )
    ax.scatter(
        df["avgval"].values,
        df.index.values,
        label="Avg",
        marker="o",
        zorder=5,
        color="yellow",
    )
    for level, row in df.iterrows():
        ax.text(
            row["max"] + 1,
            level,
            f"{row['max']:.0f} - {row['label']}",
            va="center",
        )

    ax.grid(True, color="#EEEEEE", linewidth=1)
    ax.legend(loc=1)
    ax.set_xlim(0, df["max"].max() * 1.2)
    ax.set_ylim(maxval2 - 31, maxval2 + 2)
    ax.set_ylabel(r"High Temperature $^\circ$F")
    if year == datetime.date.today().year:
        ax.set_xlabel(f"Days, {year} data till {today}")
    else:
        ax.set_xlabel("Days")

    return fig, df
