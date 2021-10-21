"""LSR ranks"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem import util
from pyiem.reference import lsr_events
from pyiem.exceptions import NoDataFound

MARKERS = ["8", ">", "<", "v", "o", "h", "*"]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 3600
    desc[
        "description"
    ] = """The National Weather Service issues Local Storm
    Reports (LSRs) with a label associated with each report indicating the
    source of the report.  This plot summarizes the number of reports
    received each year by each source type.  The values are the ranks for
    that year with 1 indicating the largest.  The values following the LSR
    event type in parenthesis are the raw LSR counts for that year. You need
    to graph at least two years worth of data to make this plot type work."""
    today = datetime.date.today()
    ltypes = list(lsr_events.keys())
    ltypes.sort()
    ev = dict(zip(ltypes, ltypes))
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(
            type="select",
            name="ltype",
            multiple=True,
            optional=True,
            options=ev,
            default="TORNADO",
            label="Select LSR Event Types: (optional)",
        ),
        dict(
            type="year",
            name="year",
            min=2006,
            default=2006,
            label="Start Year",
        ),
        dict(
            type="year",
            name="eyear",
            min=2006,
            default=today.year,
            label="End Year (inclusive)",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = util.get_dbconn("postgis")
    ctx = util.get_autoplot_context(fdict, get_description())
    ctx["_nt"].sts["_ALL"] = dict(name="All WFOs")
    station = ctx["station"][:4]
    syear = ctx["year"]
    eyear = ctx["eyear"]
    if syear == eyear:
        syear = eyear - 1
    # optional parameter, this could return null
    ltype = ctx.get("ltype")
    wfo_limiter = " and wfo = '%s' " % (
        station if len(station) == 3 else station[1:],
    )
    if station == "_ALL":
        wfo_limiter = ""
    typetext_limiter = ""
    if ltype:
        if len(ltype) == 1:
            typetext_limiter = " and typetext = '%s'" % (ltype[0],)
        else:
            typetext_limiter = " and typetext in %s" % (tuple(ltype),)

    df = read_sql(
        f"""
        select extract(year from valid)::int as yr, upper(source) as src,
        count(*) from lsrs
        where valid > '{syear}-01-01' and
        valid < '{eyear + 1}-01-01' {wfo_limiter} {typetext_limiter}
        GROUP by yr, src
    """,
        pgconn,
    )
    if df.empty:
        raise NoDataFound("No data found")
    # pivot the table so that we can fill out zeros
    df = df.pivot(index="yr", columns="src", values="count")
    df = df.fillna(0).reset_index()
    df = df.melt(id_vars="yr", value_name="count")
    df["rank"] = df.groupby(["yr"])["count"].rank(
        ascending=False, method="first"
    )
    title = "NWS %s Local Storm Report Sources Ranks" % (
        ctx["_nt"].sts[station]["name"],
    )
    if ltype:
        label = "For LSR Types: %s" % (repr(ltype),)
        if len(label) > 90:
            label = "%s..." % (label[:90],)
        title += f"\n{label}"
    (fig, ax) = figure_axes(title=title)
    # Do syear as left side
    for year in range(syear, eyear):
        dyear = df[df["yr"] == year].sort_values(by=["rank"], ascending=True)
        if not dyear.empty:
            break
        year += 1
    i = 1
    ylabels = []
    leftsrcs = []
    usedline = 0
    for _, row in dyear.iterrows():
        src = row["src"]
        leftsrcs.append(src)
        ylabels.append("%s (%.0f)" % (src, row["count"]))
        d = df[df["src"] == src].sort_values(by=["yr"])
        ax.plot(
            np.array(d["yr"]),
            np.array(d["rank"]),
            lw=2,
            label=src,
            marker=MARKERS[usedline % len(MARKERS)],
        )
        i += 1
        usedline += 1
        if i > 20:
            break
    ax.set_yticks(range(1, len(ylabels) + 1))
    ax.set_yticklabels(["%s %s" % (s, i + 1) for i, s in enumerate(ylabels)])
    ax.set_ylim(0.5, 20.5)

    ax2 = ax.twinx()
    # Do last year as right side
    dyear = df[df["yr"] == eyear].sort_values(by=["rank"], ascending=True)
    i = 0
    y2labels = []
    for _, row in dyear.iterrows():
        i += 1
        if i > 20:
            break
        src = row["src"]
        y2labels.append("%s (%.0f)" % (src, row["count"]))
        if src not in leftsrcs:
            d = df[df["src"] == src].sort_values(by=["yr"])
            ax.plot(
                np.array(d["yr"]),
                np.array(d["rank"]),
                lw=2,
                label=src,
                marker=MARKERS[usedline % len(MARKERS)],
            )
            usedline += 1

    ax2.set_yticks(range(1, len(y2labels) + 1))
    ax2.set_yticklabels(["%s %s" % (i + 1, s) for i, s in enumerate(y2labels)])
    ax2.set_ylim(0.5, 20.5)

    pos = [0.2, 0.13, 0.6, 0.75]
    ax.set_position(pos)
    ax2.set_position(pos)
    ax.set_xticks(range(df["yr"].min(), df["yr"].max(), 2))
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    ax.grid()

    fig.text(0.15, 0.88, "%s" % (syear,), fontsize=14, ha="center")
    fig.text(0.85, 0.88, "%s" % (eyear,), fontsize=14, ha="center")

    return fig, df


if __name__ == "__main__":
    plotter(dict(ltype=["SNOW"], station="PBZ"))
