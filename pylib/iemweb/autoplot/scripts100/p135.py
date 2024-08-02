"""
This plot displays the accumulated number of days
that the high or low temperature was above or below some threshold.  This uses
somewhat sloppy day-of-year logic that does not necessarily align leap years.

<p>If you split the year on 1 July, the plotted season represents the 1 July
year. ie 1 July 2023 - 30 Jun 2024 plots as 2023.</p>
"""

import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {
    "high_above": "High Temperature At or Above",
    "high_below": "High Temperature Below",
    "low_above": "Low Temperature At or Above",
    "low_below": "Low Temperature Below",
}
PDICT2 = {"jan1": "January 1", "jul1": "July 1"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="var",
            default="high_above",
            label="Which Metric",
            options=PDICT,
        ),
        dict(type="int", name="threshold", default=32, label="Threshold (F)"),
        dict(
            type="select",
            name="split",
            default="jan1",
            options=PDICT2,
            label="Where to split the year?",
        ),
        dict(
            type="year",
            name="year",
            default=datetime.date.today().year,
            label="Year to Highlight in Chart",
        ),
    ]
    return desc


def get_highcharts(ctx: dict) -> dict:
    """Highcharts Output"""
    station = ctx["station"]
    varname = ctx["var"]
    get_data(ctx)
    df = ctx["df"]

    j = {}
    j["tooltip"] = {
        "shared": True,
        "headerFormat": (
            '<span style="font-size: 10px">{point.key: %b %e}</span><br/>'
        ),
    }
    j["title"] = {
        "text": "%s [%s] %s %sF"
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            PDICT[varname],
            int(ctx.get("threshold", 32)),
        )
    }
    j["yAxis"] = {"title": {"text": "Accumulated Days"}, "startOnTick": False}
    j["xAxis"] = {
        "type": "datetime",
        "dateTimeLabelFormats": {  # don't display the dummy year
            "month": "%e. %b",
            "year": "%b",
        },
        "title": {"text": "Date"},
    }
    j["chart"] = {"zoomType": "xy", "type": "line"}
    avgs = []
    ranges = []
    thisyear = []
    for doy, row in df.iterrows():
        ts = datetime.date(2000, 1, 1) + datetime.timedelta(days=doy - 1)
        ticks = (ts - datetime.date(1970, 1, 1)).total_seconds() * 1000.0
        avgs.append([ticks, row["avg"]])
        ranges.append([ticks, row["min"], row["max"]])
        if row["thisyear"] is not None:
            thisyear.append([ticks, row["thisyear"]])
    lbl = (
        "%s" % (ctx.get("year", 2015),)
        if ctx.get("split", "jan1") == "jan1"
        else "%s - %s"
        % (int(ctx.get("year", 2015)) - 1, int(ctx.get("year", 2015)))
    )
    j["series"] = [
        {
            "name": ctx["mean_label"],
            "data": avgs,
            "zIndex": 1,
            "tooltip": {"valueDecimals": 2},
            "marker": {
                "fillColor": "white",
                "lineWidth": 2,
                "lineColor": "red",
            },
        },
        {
            "name": lbl,
            "data": thisyear,
            "zIndex": 1,
            "marker": {
                "fillColor": "blue",
                "lineWidth": 2,
                "lineColor": "green",
            },
        },
        {
            "name": "Range",
            "data": ranges,
            "type": "arearange",
            "lineWidth": 0,
            "linkedTo": ":previous",
            "color": "tan",
            "fillOpacity": 0.3,
            "zIndex": 0,
        },
    ]
    return j


def get_data(ctx):
    """Get the data"""
    station = ctx["station"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    year = ctx["year"]
    split = ctx["split"]
    opp = " < " if varname.find("_below") > 0 else " >= "
    col = "high" if varname.find("high") == 0 else "low"
    # We need to do some magic to compute the start date, since we don't want
    # an incomplete year mucking things up
    sts = ctx["_nt"].sts[station]["archive_begin"]
    if sts is None:
        raise NoDataFound("Unknown station metadata.")
    if sts.month > 1:
        sts = sts + datetime.timedelta(days=365)
        sts = sts.replace(month=1, day=1)
    doylogic = "extract(doy from day)"
    seasonlogic = "extract(year from day)"
    if split == "jul1":
        sts = sts.replace(month=7, day=1)
        doylogic = "doy_after_july1(day)"
        seasonlogic = "case when month < 7 then year - 1 else year end"
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            text(
                f"""
        with data as (
            select {seasonlogic} as season,
            {doylogic} as doy,
            (case when {col} {opp} :thres then 1 else 0 end) as hit
            from alldata where station = :sid and day >= :sts)
        SELECT season, doy,
        sum(hit) OVER (PARTITION by season ORDER by doy ASC) as hits from data
        ORDER by season ASC, doy ASC
        """
            ),
            conn,
            params={
                "sid": station,
                "thres": threshold,
                "sts": sts,
            },
            index_col=None,
        )
    if obs.empty:
        raise NoDataFound("No results returned!")
    # For all seasons that have 365 days, we need to add a 366th day by
    # repeating the last day value
    obs2 = []
    for season, gdf in obs.groupby("season"):
        if len(gdf.index) == 365:
            obs2.append(
                {"season": season, "doy": 366, "hits": gdf.iloc[-1]["hits"]}
            )
    if obs2:
        obs = pd.concat([obs, pd.DataFrame(obs2)], ignore_index=True)
    df = obs[["doy", "hits"]].groupby("doy").agg(["mean", "max", "min"]).copy()
    df.columns = ["avg", "max", "min"]
    df["datestr"] = df.index.map(
        lambda x: (
            datetime.date(2001, 1, 1) + datetime.timedelta(days=x)
        ).strftime("%-d %b")
    )
    df["thisyear"] = obs[obs["season"] == year].set_index("doy")["hits"]
    ctx["df"] = df
    ctx["mean_label"] = f"POR Average {df.iloc[-1]['avg']:.1f} days"
    ctx["obs"] = obs


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    year = ctx["year"]
    get_data(ctx)
    df = ctx["df"]
    obs = ctx["obs"]

    title = ("%s [%s]\n" r"%s %.0f$^\circ$F") % (
        ctx["_nt"].sts[station]["name"],
        station,
        PDICT[varname],
        threshold,
    )

    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.set_position([0.1, 0.1, 0.7, 0.8])
    for _season, gdf in obs.groupby("season"):
        ax.plot(
            gdf["doy"],
            gdf["hits"],
            zorder=2,
            lw=1,
            color="tan",
        )
    ax.plot(
        df.index.values,
        df["avg"],
        c="k",
        lw=2,
        zorder=3,
        label=ctx["mean_label"],
    )
    ax.plot(
        df.index.values,
        df["thisyear"],
        c="g",
        lw=2,
        zorder=3,
        label=f"{year} ({df['thisyear'].max():.0f})",
    )
    maxval = df["max"].max()
    my = obs[obs["hits"] == maxval]["season"].unique()
    df2 = obs[obs["season"] == my[-1]]
    ax.plot(
        df2["doy"],
        df2["hits"],
        c="r",
        lw=2,
        zorder=3,
        label=f"Most {my[-1]:.0f}{'+' if len(my) > 1 else ''} ({maxval:.0f})",
    )
    df2 = obs[obs["doy"] == 366]
    minval = df2["hits"].min()
    my = df2[df2["hits"] == minval]["season"].unique()
    df2 = obs[obs["season"] == my[-1]]
    ax.plot(
        df2["doy"],
        df2["hits"],
        c="b",
        lw=2,
        zorder=3,
        label=f"Least {my[-1]:.0f}{'+' if len(my) > 1 else ''} ({minval:.0f})",
    )

    ax.legend(ncol=1, loc=2)
    xticks = []
    xticklabels = []
    for x in range(int(df.index.min()) - 1, int(df.index.max())):
        ts = datetime.date(
            2000, 7 if ctx["split"] == "jul1" else 1, 1
        ) + datetime.timedelta(days=x)
        if ts.day == 1:
            xticks.append(x)
            xticklabels.append(ts.strftime("%b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.grid(True)
    ax.set_xlim(int(df.index.min()) - 1, int(df.index.max()) + 1)
    ax.set_ylim(bottom=-1)
    ax.set_ylabel("Accumulated Days")

    ss = (
        obs[["season", "hits"]]
        .groupby("season")
        .agg("max")
        .sort_values(by="hits", ascending=False)
    )
    # ------------------------
    txt = "Top 10 (Full Year)   \n\n"
    for season, row in ss.head(10).iterrows():
        txt += f"{season:.0f} {row['hits']:.0f}\n"

    # put text into a pretty rounded text box
    fig.text(
        0.83,
        0.7,
        txt[:-1],
        bbox=dict(boxstyle="round", facecolor="r", alpha=0.4),
        va="center",
        ha="left",
    )

    # ------------------------
    txt = "Bottom 10 (Full Year)\n\n"
    for season, row in ss.iloc[::-1].head(10).iterrows():
        txt += f"{season:.0f} {row['hits']:.0f}\n"

    # put text into a pretty rounded text box
    fig.text(
        0.83,
        0.3,
        txt[:-1],
        bbox=dict(boxstyle="round", facecolor="r", alpha=0.4),
        va="center",
        ha="left",
    )
    return fig, df
