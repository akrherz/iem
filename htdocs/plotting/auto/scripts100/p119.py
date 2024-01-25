"""
This chart presents the accumulated frequency of a temperature threshold being
the first time observed or last time observed during the fall season. There is
a complexitiy to the last time metric as it is somewhat undefined as to when
the fall season ends and the next spring/summer season beings.  So life choices
are made here:</p>

<p>For <strong>first below</strong>, the first date that the temperature
happens is considered between 1 August and 31 May of the next year. This is
generally straight forward.</p>

<p>For <strong>last above</strong>, the last date that the temperature happens
is considered between 1 August and 31 December of the same year. This is
nebulous for temperature thresholds that are common throughout the cold
season. Caveat emptor.</p>

<p><a href="/plotting/auto/?q=120">Autoplot 120</a> is closely related to this
autoplot and presents the spring season values.</p>
"""
import datetime

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "era5land_soilt4_avg": "ERA5Land 0-10cm Avg Soil Temp",
    "low": "Low Temperature",
    "high": "High Temperature",
}
PDICT2 = {
    "first_below": "First Fall Temperature at or below Threshold",
    "last_above": "Last Fall Temperature at or above Threshold",
}


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
        {
            "type": "select",
            "name": "opt",
            "default": "first_below",
            "label": "Which metric to compute?",
            "options": PDICT2,
        },
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
    opt = ctx["opt"]
    station = ctx["station"]
    bs = ctx["_nt"].sts[station]["archive_begin"]
    if bs is None:
        raise NoDataFound("Unknown metadata")
    thresholds = [ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"]]
    # Ensure that thresholds are unique
    if len(thresholds) != len(set(thresholds)):
        raise NoDataFound("Thresholds need to be unique.")

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
    comp = "<=" if opt == "first_below" else ">="
    months = [8, 9, 10, 11, 12]
    quorum = 150
    if opt == "first_below":
        months = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5]
        quorum = 300
    sent = "2099-01-01" if opt == "first_below" else "1800-01-01"
    with get_sqlalchemy_conn("coop") as conn:
        for i, base in enumerate(thresholds):
            # Find first dates by winter season
            df2 = pd.read_sql(
                f"""
                select
                case when month > 7 then year + 1 else year end as winter,
                {'min' if opt == 'first_below' else 'max'}(
                case when {ctx["var"]} {comp}
                %s then day else '{sent}'::date end) as date,
                count(*) from alldata
                WHERE station = %s and month = ANY(%s)
                GROUP by winter
            """,
                conn,
                params=(base, station, months),
                index_col=None,
            )
            if df2.empty:
                raise NoDataFound("No Data Found.")
            # Require quorum
            df2 = df2[df2["count"] > quorum]
            if df2.empty:
                raise NoDataFound("No Data Found.")
            df2["doy"] = np.nan
            for idx, row in df2.iterrows():
                if row["date"].year in [2099, 1800]:
                    continue
                jan1 = datetime.date(row["winter"] - 1, 1, 1)
                doy = (row["date"] - jan1).days
                df2.at[idx, "doy"] = doy
                df.loc[doy:sz, f"{base}cnts"] += 1
            mindates[i] = df2.sort_values(
                "doy", ascending=True, na_position="last"
            ).iloc[0]["date"]
            # Ensure that all doys are filled in
            if df2["doy"].notna().all():
                maxdates[i] = df2.sort_values(
                    "doy", ascending=False, na_position="last"
                ).iloc[0]["date"]

            df[f"{base}freq"] = df[f"{base}cnts"] / len(df2.index) * 100.0
    explainer = (
        "On a certain date, what is the observed frequency that a given\n"
        "temperature threshold has been first observed by the given date."
    )
    if opt == "last_above":
        explainer = (
            "On a certain date, what is the observed frequency that a given\n"
            "temperature threshold has been observed for the last time."
        )
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {datetime.date.today():%d %b %Y}\n"
        f"# Climate Record: {bs} -> {datetime.date.today()}\n"
        f"# Site Information: {ctx['_sname']}\n"
        "# Contact: Daryl Herzmann akrherz@iastate.edu 515.294.5978\n"
        f"# {PDICT[ctx['var']]} exceedence probabilities\n"
        f"# {explainer}\n"
        f" DOY Date    {comp}{thresholds[0]}  {comp}{thresholds[1]}  "
        f"{comp}{thresholds[2]}  {comp}{thresholds[3]}\n"
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
    if mindate is None:
        raise NoDataFound("Error found, try different thresholds.")
    if maxdate is None:
        maxdate = datetime.datetime(2001, 6, 1)

    byear = bs.year
    if ctx["var"] == "era5land_soilt4_avg":
        byear = max(1951, byear)
    title = ("Frequency of %s\n%s %s (%s-%s)") % (
        PDICT2[opt].replace("Temperature", PDICT[ctx["var"]]),
        station,
        ctx["_nt"].sts[station]["name"],
        byear,
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
        if df[f"{base}freq"].min() == 0:
            celltext[0][i] = mindates[i].strftime("%b %d\n%Y")
            cellcolors[0][i] = colors[mindates[i].month - 1]
        if df[f"{base}freq"].max() >= 100 and maxdates[i] is not None:
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
    plotter({})
