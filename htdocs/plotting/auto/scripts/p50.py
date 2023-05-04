"""This app produces a table of frequencies of
    wind and hail tags used in NWS Severe Thunderstorm Warnings. You have the
    choice to only plot the issuance or use a computed max value over the
    warning's lifecycle (including SVSs).  The maximum wind and hail tags
    are computed independently over the lifecycle of the Severe Thunderstorm
    Warning."""
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {"state": "Aggregate by State", "wfo": "Aggregate by WFO"}
PDICT2 = {"percent": "Frequency [%]", "count": "Count"}
PDICT3 = {
    "issuance": "Only Issuance Considered",
    "max": "Computed Max over SVR+SVS",
}
FONTSIZE = 12


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 300}
    today = datetime.datetime.today() + datetime.timedelta(days=1)

    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="_ALL",
            label="Select WFO:",
            all=True,
        ),
        dict(type="state", name="state", default="IA", label="Select State:"),
        dict(
            type="select",
            name="opt",
            default="wfo",
            label="Plot for WFO(all option) or State:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="p",
            default="percent",
            label="What to plot:",
            options=PDICT2,
        ),
        dict(
            type="select",
            options=PDICT3,
            default="issuance",
            label="How should SVS updates be considered?",
            name="agg",
        ),
        dict(
            type="date",
            name="date1",
            optional=True,
            default="2010/04/01",
            label="Start Date Bounds (optional):",
            min="2010/04/01",
        ),
        dict(
            type="date",
            name="date2",
            optional=True,
            default=today.strftime("%Y/%m/%d"),
            label="End Date Bounds (optional):",
            min="2010/04/01",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}

    opt = ctx["opt"]
    station = ctx["station"]
    state = ctx["state"]
    date1 = ctx.get("date1", datetime.date(2010, 4, 1))
    date2 = ctx.get(
        "date2", datetime.date.today() + datetime.timedelta(days=1)
    )
    wfo_limiter = (
        f"and wfo = '{station if len(station) == 3 else station[1:]}' "
    )
    if station == "_ALL":
        wfo_limiter = ""
    status_limiter = "and status = 'NEW'"
    if ctx["agg"] == "max":
        status_limiter = ""
    sql = f"""
    WITH data as (
        SELECT wfo, eventid, extract(year from polygon_begin) as year,
        min(polygon_begin) as min_issue,
        max(windtag) as max_windtag, max(hailtag) as max_hailtag
        from sbw WHERE polygon_begin >= %s and
        polygon_begin <= %s {wfo_limiter}
        and (windtag > 0 or hailtag > 0) and phenomena = 'SV' and
        significance = 'W' {status_limiter} GROUP by wfo, eventid, year
    )
    select max_windtag as windtag, max_hailtag as hailtag,
    min(min_issue at time zone 'UTC') as min_issue,
    max(min_issue at time zone 'UTC') as max_issue, count(*)
    from data GROUP by windtag, hailtag
    """
    args = (date1, date2)
    supextra = ""
    if opt == "wfo" and station != "_ALL":
        supextra = (
            f"For warnings issued by {station} "
            f"{ctx['_nt'].sts[station]['name']}.\n"
        )
    if opt == "state":
        supextra = (
            "For warnings that covered some portion of "
            f"{state_names[state]}.\n"
        )

        sql = f"""
        WITH data as (
            SELECT wfo, eventid, extract(year from polygon_begin) as year,
            min(polygon_begin) as min_issue,
            max(windtag) as max_windtag, max(hailtag) as max_hailtag
            from sbw w, states s
            WHERE polygon_begin >= %s and polygon_begin <= %s and
            s.state_abbr = %s and ST_Intersects(s.the_geom, w.geom)
            and (windtag > 0 or hailtag > 0) and phenomena = 'SV' and
            significance = 'W' {status_limiter} GROUP by wfo, eventid, year
        )
        select max_windtag as windtag, max_hailtag as hailtag,
        min(min_issue at time zone 'UTC') as min_issue,
        max(min_issue at time zone 'UTC') as max_issue, count(*)
        from data GROUP by windtag, hailtag
        """
        args = (date1, date2, state)
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(sql, conn, params=args, index_col=None)
    if df.empty:
        raise NoDataFound("No data was found.")
    minvalid = df["min_issue"].min()
    maxvalid = df["max_issue"].max()
    df = df.fillna(0)
    total = df["count"].sum()
    uniquehail = df["hailtag"].unique().tolist()
    uniquehail.sort()
    uniquehail = uniquehail[::-1]
    uniquewind = df["windtag"].astype(int).unique().tolist()
    uniquewind.sort()

    gdf = df.set_index(["hailtag", "windtag"])

    (fig, ax) = figure_axes(apctx=ctx)
    for (hailtag, windtag), row in gdf.iterrows():
        y = uniquehail.index(hailtag)
        x = uniquewind.index(windtag)
        val = row["count"] / total * 100.0
        ax.text(
            x,
            y,
            f"{val:.2f}" if ctx["p"] == "percent" else row["count"],
            ha="center",
            fontsize=FONTSIZE,
            color="r" if val >= 10 else "k",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
        )

    for htag, row in df.groupby("hailtag").sum(numeric_only=True).iterrows():
        y = uniquehail.index(htag)
        x = len(uniquewind)
        val = row["count"] / total * 100.0
        ax.text(
            x,
            y,
            f"{val:.2f}" if ctx["p"] == "percent" else int(row["count"]),
            ha="center",
            fontsize=FONTSIZE,
            color="r" if val >= 10 else "k",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
        )

    for wtag, row in df.groupby("windtag").sum(numeric_only=True).iterrows():
        y = -1
        x = uniquewind.index(wtag)
        val = row["count"] / total * 100.0
        ax.text(
            x,
            y,
            f"{val:.2f}" if ctx["p"] == "percent" else int(row["count"]),
            ha="center",
            fontsize=FONTSIZE,
            color="r" if val >= 10 else "k",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
        )

    ax.set_xticks(range(len(uniquewind) + 1))
    ax.set_yticks(range(-1, len(uniquehail)))
    ax.set_xlim(-0.5, len(uniquewind) + 0.5)
    ax.set_ylim(-1.5, len(uniquehail) - 0.5)
    ax.set_xticklabels(uniquewind + ["Total"], fontsize=14)
    ax.set_yticklabels(["Total"] + uniquehail, fontsize=14)
    ax.xaxis.tick_top()
    ax.set_xlabel("Wind Speed [mph]", fontsize=14)
    ax.set_ylabel("Hail Size [inch]", fontsize=14)
    ax.xaxis.set_label_position("top")
    plt.tick_params(top=False, bottom=False, left=False, right=False)
    fig.suptitle(
        f"{PDICT2[ctx['p']]} of NWS Wind/Hail Tags for Svr Tstorm Warn "
        f"{PDICT3[ctx['agg']]}\n"
        f"{minvalid:%-d %b %Y} through {maxvalid:%-d %b %Y}, "
        f"{df['count'].sum():.0f} warnings\n{supextra}"
        "Values larger than 10% in red"
    )
    ax.set_position([0.12, 0.05, 0.86, 0.72])

    return fig, df


if __name__ == "__main__":
    plotter({})
