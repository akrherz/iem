"""Days at or above temperature level"""
import datetime

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound

PDICT = {
    "full": "Show Full Year Totals",
    "ytd": "Limit to Year to Date Period",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot shows the number of days with a high
    temperature at or above a given threshold.  You can optionally generate
    this plot for the year to date period.
    """
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
    today = datetime.date.today()
    if limit == "ytd":
        limittitle = "(Jan 1 - %s)" % (today.strftime("%b %-d"),)
        limitsql = " and extract(doy from day) <= %s" % (today.strftime("%j"),)

    dbconn = get_dbconn("coop")

    table = "alldata_%s" % (station[:2],)
    df = read_sql(
        f"SELECT year, day, high from {table} WHERE station = %s and "
        f"high is not null {limitsql} ORDER by day ASC",
        dbconn,
        params=(station,),
        index_col="day",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    res = []
    maxval2 = int(df["high"].max())
    for level in range(maxval2 - 30, maxval2 + 2):
        gdf = df[df["high"] >= level].groupby("year").count()
        maxval = gdf.max()[0]
        label = ",".join(
            [str(s) for s in list(gdf[gdf["high"] == maxval].index.values)]
        )
        thisyear = 0
        if year in gdf.index.values:
            thisyear = gdf.at[year, "high"]
        res.append(
            dict(level=level, label=label, max=maxval, thisyear=thisyear)
        )

    df = pd.DataFrame(res)
    df = df.set_index("level")

    (fig, ax) = figure_axes(apctx=ctx)
    ax.barh(df.index.values, df["max"].values, label="Max", zorder=2)
    ax.barh(
        df.index.values, df["thisyear"].values, label="%s" % (year,), zorder=3
    )
    for level, row in df.iterrows():
        ax.text(
            row["max"] + 1,
            level,
            "%.0f - %s" % (row["max"], row["label"]),
            va="center",
        )

    ax.grid(True, color="#EEEEEE", linewidth=1)
    ax.legend(loc="best")
    ax.set_xlim(0, df["max"].max() * 1.2)
    ax.set_ylim(maxval2 - 31, maxval2 + 2)
    ax.set_title(
        (
            "%s Max Days per Year %s\n"
            "at or above given high temperature threshold"
        )
        % (ctx["_nt"].sts[station]["name"], limittitle)
    )
    ax.set_ylabel(r"High Temperature $^\circ$F")
    if year == datetime.date.today().year:
        ax.set_xlabel(("Days, %s data through %s") % (year, today))
    else:
        ax.set_xlabel("Days")

    return fig, df


if __name__ == "__main__":
    plotter({})
