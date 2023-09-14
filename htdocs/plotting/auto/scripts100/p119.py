"""
This chart presents the accumulated frequency of
having the first fall temperature at or below a given threshold.
"""
import datetime

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {"low": "Low Temperature", "high": "High Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            options=PDICT,
            name="var",
            default="low",
            label="Select variable to summarize:",
        ),
        dict(type="int", name="t1", default=32, label="First Threshold (F)"),
        dict(type="int", name="t2", default=28, label="Second Threshold (F)"),
        dict(type="int", name="t3", default=26, label="Third Threshold (F)"),
        dict(type="int", name="t4", default=22, label="Fourth Threshold (F)"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown metadata")
    thresholds = [ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]]

    sz = 214 + 304
    df = pd.DataFrame(
        {
            "dates": pd.date_range("2000/08/01", "2001/05/31"),
            f"{thresholds[0]}cnts": 0,
            f"{thresholds[1]}cnts": 0,
            f"{thresholds[2]}cnts": 0,
            f"{thresholds[3]}cnts": 0,
        },
        index=range(214, sz),
    )
    df.index.name = "doy"

    mindates = [None, None, None, None]
    maxdates = [None, None, None, None]
    with get_sqlalchemy_conn("coop") as conn:
        for i, base in enumerate(thresholds):
            # Find first dates by winter season
            df2 = pd.read_sql(
                f"""
                select
                case when month > 7 then year + 1 else year end as winter,
                min(case when {ctx["var"]} <= %s
                then day else '2099-01-01'::date end) as mindate from alldata
                WHERE station = %s and month not in (6, 7) and year < %s
                GROUP by winter
            """,
                conn,
                params=(base, station, datetime.date.today().year),
                index_col=None,
            )
            if df2.empty:
                raise NoDataFound("No Data Found.")
            df2["doy"] = np.nan
            for idx, row in df2.iterrows():
                if row["mindate"].year == 2099:
                    continue
                jan1 = datetime.date(row["winter"] - 1, 1, 1)
                doy = (row["mindate"] - jan1).days
                df2.at[idx, "doy"] = doy
                df.loc[doy:sz, f"{base}cnts"] += 1
            mindates[i] = df2.sort_values(
                "doy", ascending=True, na_position="last"
            ).iloc[0]["mindate"]
            maxdates[i] = df2.sort_values(
                "doy", ascending=False, na_position="last"
            ).iloc[0]["mindate"]

            df[f"{base}freq"] = df[f"{base}cnts"] / len(df2.index) * 100.0

    res = """\
# IEM Climodat https://mesonet.agron.iastate.edu/climodat/
# Report Generated: %s
# Climate Record: %s -> %s
# Site Information: [%s] %s
# Contact Information: Daryl Herzmann akrherz@iastate.edu 515.294.5978
# %s exceedence probabilities
# (On a certain date, what is the chance a temperature below a certain
# threshold would have been observed once already during the fall of that year)
 DOY Date    <%s  <%s  <%s  <%s
""" % (
        datetime.date.today().strftime("%d %b %Y"),
        bs,
        datetime.date.today(),
        station,
        ctx["_nt"].sts[station]["name"],
        PDICT[ctx["var"]],
        thresholds[0] + 1,
        thresholds[1] + 1,
        thresholds[2] + 1,
        thresholds[3] + 1,
    )
    fcols = [f"{s}freq" for s in thresholds]
    mindate = None
    maxdate = None
    for doy, row in df.iterrows():
        if doy % 2 != 0:
            continue
        if row[fcols[3]] >= 100:
            if maxdate is None:
                maxdate = row["dates"] + datetime.timedelta(days=5)
            continue
        if row[fcols[0]] > 0 and mindate is None:
            mindate = row["dates"] - datetime.timedelta(days=5)
        res += (" %3s %s  %3i  %3i  %3i  %3i\n") % (
            row["dates"].strftime("%-j"),
            row["dates"].strftime("%b %d"),
            row[fcols[0]],
            row[fcols[1]],
            row[fcols[2]],
            row[fcols[3]],
        )
    if maxdate is None:
        maxdate = datetime.datetime(2001, 6, 1)

    title = (
        "Frequency of First Fall %s At or Below Threshold\n%s %s (%s-%s)"
    ) % (
        PDICT[ctx["var"]],
        station,
        ctx["_nt"].sts[station]["name"],
        bs.year,
        datetime.date.today().year,
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    # shrink the plot to make room for the table
    ax.set_position([0.1, 0.1, 0.6, 0.8])
    for base in thresholds:
        ax.plot(
            df["dates"].values,
            df[f"{base}freq"].values,
            label=f"{base}",
            lw=2,
        )

    ax.legend(loc="best")
    ax.set_xlim(mindate, maxdate)
    days = (maxdate - mindate).days
    dl = [1] if days > 120 else [1, 7, 14, 21]
    ax.xaxis.set_major_locator(mdates.DayLocator(dl))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    ax.grid(True)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_ylabel("Accumulated to Date Frequency [%]")

    # Create the cell text as an enpty list of 4 columns by 11 rows
    celltext = [[""] * 4 for _ in range(11)]
    cellcolors = [["white"] * 4 for _ in range(11)]
    # create 12 jet colors to use to color the cells by month of the year
    colors = plt.cm.jet(np.arange(12) / 12.0)
    # set the alpha to 0.5
    colors[:, -1] = 0.5

    # compute the dates for each threshold having 10 thru 90% frequency
    for i, base in enumerate(thresholds):
        celltext[0][i] = mindates[i].strftime("%b %d\n%Y")
        cellcolors[0][i] = colors[mindates[i].month - 1]
        if df[f"{base}freq"].max() >= 100:
            celltext[-1][i] = maxdates[i].strftime("%b %d\n%Y")
            cellcolors[-1][i] = colors[maxdates[i].month - 1]

        for j, percent in enumerate(range(10, 100, 10), start=1):
            df2 = df[df[f"{base}freq"] >= percent]
            if df2.empty:
                continue
            row = df2.iloc[0]
            celltext[j][i] = row["dates"].strftime("%b %d")
            cellcolors[j][i] = colors[row["dates"].month - 1]

    ax2 = fig.add_axes([0.75, 0.1, 0.2, 0.75])
    # remove all the splines, but show the ylabel
    ax2.spines["top"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.set_xticks([])
    ax2.set_yticks([])
    table = ax2.table(
        celltext,
        cellColours=cellcolors,
        colLabels=[f"{t}" + r"$^\circ$F" for t in thresholds],
        rowLabels=["Min"] + list(range(10, 100, 10)) + ["Max"],
        loc="center",
    )
    # add some vertical padding to text in the table and keep the borders
    for cell in table.properties()["celld"].values():
        cell.set_height(0.08)

    fig.text(0.85, 0.85, "Percentile Dates", ha="center")

    return fig, df.reset_index(), res


if __name__ == "__main__":
    plotter({"station": "IA0070"})
