"""IBW Tag Freq."""
import datetime

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"state": "Aggregate by State", "wfo": "Aggregate by WFO"}
FONTSIZE = 12


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 300
    desc[
        "description"
    ] = """This app produces a table of frequencies of
    wind and hail tags used in NWS Warnings."""
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
            label="Start Date Bounds (optional):",
            min="2010/04/01",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}

    opt = ctx["opt"]
    station = ctx["station"]
    state = ctx["state"]
    date1 = ctx.get("date1", datetime.date(2010, 4, 1))
    date2 = ctx.get(
        "date2", datetime.date.today() + datetime.timedelta(days=1)
    )
    pgconn = get_dbconn("postgis")
    wfo_limiter = ("and wfo = '%s' ") % (
        station if len(station) == 3 else station[1:],
    )
    if station == "_ALL":
        wfo_limiter = ""
    sql = """
    select windtag, hailtag,
    min(issue at time zone 'UTC') as min_issue,
    max(issue at time zone 'UTC') as max_issue, count(*)
    from sbw WHERE issue >= '%s' and issue <= '%s'
    %s
    and (windtag > 0 or hailtag > 0)
    and status = 'NEW' and phenomena = 'SV'
    GROUP by windtag, hailtag
    """ % (
        date1,
        date2,
        wfo_limiter,
    )
    supextra = ""
    if opt == "wfo" and station != "_ALL":
        supextra = "For warnings issued by %s %s.\n" % (
            station,
            ctx["_nt"].sts[station]["name"],
        )
    if opt == "state":
        supextra = ("For warnings that covered some portion of %s.\n") % (
            state_names[state],
        )

        sql = """
        SELECT windtag, hailtag,
        min(issue at time zone 'UTC') as min_issue,
        max(issue at time zone 'UTC') as max_issue, count(*)
        from sbw w, states s
        WHERE issue >= '%s' and issue <= '%s' and
        s.state_abbr = '%s' and ST_Intersects(s.the_geom, w.geom) and
        (windtag > 0 or hailtag > 0)
        and status = 'NEW' and phenomena = 'SV'
        GROUP by windtag, hailtag
        """ % (
            date1,
            date2,
            state,
        )

    df = read_sql(sql, pgconn, index_col=None)
    if df.empty:
        raise NoDataFound("No data was found.")
    minvalid = df["min_issue"].min()
    maxvalid = df["max_issue"].max()
    df.fillna(0, inplace=True)
    total = df["count"].sum()
    uniquehail = df["hailtag"].unique().tolist()
    uniquehail.sort()
    uniquehail = uniquehail[::-1]
    uniquewind = df["windtag"].astype(int).unique().tolist()
    uniquewind.sort()

    gdf = df.set_index(["hailtag", "windtag"])

    (fig, ax) = plt.subplots(figsize=(8, 6))
    for (hailtag, windtag), row in gdf.iterrows():
        y = uniquehail.index(hailtag)
        x = uniquewind.index(windtag)
        val = row["count"] / total * 100.0
        ax.text(
            x,
            y,
            "%.2f" % (val,),
            ha="center",
            fontsize=FONTSIZE,
            color="r" if val >= 10 else "k",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
        )

    for hailtag, row in df.groupby("hailtag").sum().iterrows():
        y = uniquehail.index(hailtag)
        x = len(uniquewind)
        val = row["count"] / total * 100.0
        ax.text(
            x,
            y,
            "%.2f" % (val,),
            ha="center",
            fontsize=FONTSIZE,
            color="r" if val >= 10 else "k",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
        )

    for windtag, row in df.groupby("windtag").sum().iterrows():
        y = -1
        x = uniquewind.index(windtag)
        val = row["count"] / total * 100.0
        ax.text(
            x,
            y,
            "%.2f" % (val,),
            ha="center",
            fontsize=FONTSIZE,
            color="r" if val >= 10 else "k",
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
        )

    ax.set_xticks(range(len(uniquewind) + 1))
    ax.set_yticks(range(-1, len(uniquehail) + 1))
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
        (
            "Frequency [%%] of NWS Wind/Hail Tags for "
            "Severe Thunderstorm Warning Issuance\n"
            "%s through %s, %.0f warnings\n%s"
            "Values larger than 10%% in red"
        )
        % (
            minvalid.strftime("%d %b %Y"),
            maxvalid.strftime("%d %b %Y"),
            df["count"].sum(),
            supextra,
        )
    )
    ax.set_position([0.15, 0.05, 0.8, 0.72])

    return fig, df


if __name__ == "__main__":
    plotter(dict())
