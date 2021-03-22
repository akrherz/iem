"""
Heat Advisory and Wind Chill alerts by temperature.
"""

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.nws.vtec import NWS_COLORS, get_ps_string
from pyiem.exceptions import NoDataFound

PDICT = {
    "no": "Consider all Heat Index / Wind Chill Values",
    "yes": "Only consider additive cases, with index worse than temperature",
}
PDICT2 = {"heat": "Heat Index", "chill": "Wind Chill"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 3600
    desc[
        "description"
    ] = """This plot presents a frequency of having either a heat index
    or wind chill advisory/warning active for a given computed feels like
    temperature.  The major caveat with this plot is that it does not address
    the duration requirement that these alerts carry with them.  For example,
    instantaneously dipping to a wind chill of -20 does not necessarily
    necessitate a wind chill advisory be issued.  Another tunable knob to
    this application is to only consider 'additive' cases.  That being when
    the wind chill is colder than the air temperature and when the heat index
    is higher than the air temperature.  In the case of wind chill, a calm
    wind can lead to a nebulous wind chill.  Similiarly, a low humidity to
    what the computed heat index is.</p>

    <p>The plot shows the NWS headline frequency for the forecast zone that
    the automated weather station resides in."""
    desc["arguments"] = [
        dict(
            type="zstation",
            name="station",
            default="AMW",
            network="IA_ASOS",
            label="Select station:",
        ),
        dict(
            type="select",
            options=PDICT,
            default="no",
            name="opt",
            label="Should observations be limited?",
        ),
        dict(
            type="select",
            options=PDICT2,
            default="heat",
            name="var",
            label="Which feels like temperature to plot?",
        ),
    ]
    return desc


def get_df(ctx):
    """Figure out what data we need to fetch here"""
    ctx["ugc"] = ctx["_nt"].sts[ctx["station"]]["ugc_zone"]
    pgconn = get_dbconn("postgis")
    ctx["s1"] = "Y"
    ctx["s2"] = "W"
    if ctx["var"] == "heat":
        ctx["p1"] = "HT"
        ctx["p2"] = "EH"
    else:
        ctx["p1"] = "WC"
        ctx["p2"] = "WC"
    # Thankfully, all the above are zone based
    events = read_sql(
        """
        SELECT generate_series(issue, expire, '1 minute'::interval) as valid,
        (phenomena ||'.'|| significance) as vtec
        from warnings WHERE ugc = %s and (
            (phenomena = %s and significance = %s) or
            (phenomena = %s and significance = %s)
        ) ORDER by issue ASC
    """,
        pgconn,
        params=(ctx["ugc"], ctx["p1"], ctx["s1"], ctx["p2"], ctx["s2"]),
        index_col="valid",
    )
    if events.empty:
        raise NoDataFound("No Alerts were found for UGC: %s" % (ctx["ugc"],))
    pgconn = get_dbconn("asos")
    thres = "tmpf > 70" if ctx["var"] == "heat" else "tmpf < 40"
    obs = read_sql(
        "SELECT valid, tmpf::int as tmpf, feel from alldata where "
        f"station = %s and valid > %s and {thres} and feel is not null "
        "ORDER by valid ASC",
        pgconn,
        params=(ctx["station"], str(events.index.values[0])),
        index_col="valid",
    )
    ctx["title"] = (
        "%s [%s] (%s to %s)\n" "Frequency of NWS Headline for %s by %s"
    ) % (
        ctx["_nt"].sts[ctx["station"]]["name"],
        ctx["station"],
        str(events.index.values[0])[:10],
        str(obs.index.values[-1])[:10],
        ctx["ugc"],
        PDICT2[ctx["var"]],
    )
    if ctx["opt"] == "yes":
        if ctx["var"] == "heat":
            obs = obs[obs["feel"] > obs["tmpf"]]
        else:
            obs = obs[obs["feel"] < obs["tmpf"]]
    obs["feel"] = obs["feel"].round(0)
    res = obs.join(events).fillna("None")
    counts = res[["feel", "vtec"]].groupby(["feel", "vtec"]).size()
    df = pd.DataFrame(counts)
    df.columns = ["count"]
    ctx["df"] = (
        df.reset_index()
        .pivot(index="feel", columns="vtec", values="count")
        .fillna(0)
    )
    ctx["df"]["Total"] = ctx["df"].sum(axis=1)
    for vtec in [
        "%s.%s" % (ctx["p1"], ctx["s1"]),
        "%s.%s" % (ctx["p2"], ctx["s2"]),
        "None",
    ]:
        if vtec not in ctx["df"].columns:
            ctx["df"][vtec] = 0.0
        ctx["df"][vtec + "%"] = ctx["df"][vtec] / ctx["df"]["Total"] * 100.0


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())

    get_df(ctx)
    (fig, ax) = plt.subplots()

    v1 = "%s.%s" % (ctx["p1"], ctx["s1"])
    hty = ctx["df"][v1 + "%"]
    ax.bar(
        ctx["df"].index.values,
        hty,
        label=get_ps_string(ctx["p1"], ctx["s1"]),
        color=NWS_COLORS[v1],
    )

    v2 = "%s.%s" % (ctx["p2"], ctx["s2"])
    ehw = ctx["df"][v2 + "%"]
    ax.bar(
        ctx["df"].index.values,
        ehw.values,
        bottom=hty.values,
        label=get_ps_string(ctx["p2"], ctx["s2"]),
        color=NWS_COLORS[v2],
    )
    non = ctx["df"]["None%"]
    ax.bar(
        ctx["df"].index.values,
        non,
        bottom=(hty + ehw).values,
        label="No Headline",
        color="#EEEEEE",
    )
    ax.legend(loc=(-0.03, -0.22), ncol=3)
    ax.set_position([0.1, 0.2, 0.8, 0.7])
    ax.grid(True)
    ax.set_xlabel(
        (r"Feels Like $^\circ$F, %s")
        % ("All Obs Considered" if ctx["opt"] == "no" else "Only Additive Obs")
    )
    ax.set_ylabel("Frequency [%]")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_title(ctx["title"])

    # Clip the plot in the case of wind chill
    if ctx["var"] == "chill":
        vals = non[non < 100]
        if len(vals.index) > 0:
            ax.set_xlim(right=vals.index.values[-1] + 2)

    return fig, ctx["df"]


if __name__ == "__main__":
    plotter(dict(opt="no", var="chill"))
