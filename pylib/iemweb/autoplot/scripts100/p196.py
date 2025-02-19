"""
This plot presents a frequency of having either a heat index
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

<p>For the winter season of 2024-2025, the National Weather Service changed
to issue Extreme Cold Warning and Cold Weather Advisory instead of
Wind Chill Advisories/Warnings.</p>

<p>The plot shows the NWS headline frequency for the forecast zone that
the automated weather station resides in.
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws.vtec import NWS_COLORS, get_ps_string
from pyiem.plot import figure_axes

PDICT = {
    "no": "Consider all Heat Index / Wind Chill Values",
    "yes": "Only consider additive cases, with index worse than temperature",
}
PDICT2 = {
    "heat": "Heat Index",
    "chill": "Wind Chill (pre 2024/2025)",
    "chill25": "Wind Chill (2024/2025 +)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 3600}
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
    ctx["s1"] = "Y"
    ctx["s2"] = "W"
    tlimit = ""
    if ctx["var"] == "heat":
        ctx["p1"] = "HT"
        ctx["p2"] = "EH"
    elif ctx["var"] == "chill":
        ctx["p1"] = "WC"
        ctx["p2"] = "WC"
        tlimit = " and issue < '2024-09-01' "
    else:
        ctx["p1"] = "CW"
        ctx["p2"] = "EC"
        tlimit = " and issue > '2024-09-01' "
    # Thankfully, all the above are zone based
    with get_sqlalchemy_conn("postgis") as conn:
        events = pd.read_sql(
            sql_helper(
                """
            SELECT generate_series(issue, expire, '1 minute'::interval)
            as valid,
            (phenomena ||'.'|| significance) as vtec
            from warnings WHERE ugc = :ugc and (
                (phenomena = :p1 and significance = :s1) or
                (phenomena = :p2 and significance = :s2) {tlimit}
            ) ORDER by issue ASC
        """,
                tlimit=tlimit,
            ),
            conn,
            params={
                "ugc": ctx["ugc"],
                "p1": ctx["p1"],
                "s1": ctx["s1"],
                "p2": ctx["p2"],
                "s2": ctx["s2"],
            },
            index_col="valid",
        )
    if events.empty:
        raise NoDataFound(f"No Alerts were found for UGC: {ctx['ugc']}")
    thres = "tmpf > 70" if ctx["var"] == "heat" else "tmpf < 40"
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            sql_helper(
                """
    SELECT valid, tmpf::int as tmpf, feel from alldata where
    station = :station and valid > :sts and {thres} and feel is not null
    {tlimit}
    ORDER by valid ASC""",
                thres=thres,
                tlimit=tlimit.replace("issue", "valid"),
            ),
            conn,
            params={
                "station": ctx["station"],
                "sts": str(events.index.values[0]),
            },
            index_col="valid",
        )
    if obs.empty:
        raise NoDataFound("No Data Found.")
    ctx["title"] = (
        f"{ctx['_sname']} ({str(events.index.values[0])[:10]} "
        f"to {str(obs.index.values[-1])[:10]})\n"
        f"Frequency of NWS Headline for {ctx['ugc']} by {PDICT2[ctx['var']]}"
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
        f"{ctx['p1']}.{ctx['s1']}",
        f"{ctx['p2']}.{ctx['s2']}",
        "None",
    ]:
        if vtec not in ctx["df"].columns:
            ctx["df"][vtec] = 0.0
        ctx["df"][f"{vtec}%"] = ctx["df"][vtec] / ctx["df"]["Total"] * 100.0


def plotter(ctx: dict):
    """Go"""
    get_df(ctx)
    (fig, ax) = figure_axes(apctx=ctx)

    v1 = f"{ctx['p1']}.{ctx['s1']}"
    hty = ctx["df"][v1 + "%"]
    ax.bar(
        ctx["df"].index.values,
        hty,
        label=get_ps_string(ctx["p1"], ctx["s1"]),
        color=NWS_COLORS[v1],
    )

    v2 = f"{ctx['p2']}.{ctx['s2']}"
    ehw = ctx["df"][f"{v2}%"]
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
    _tt = "All Obs Considered" if ctx["opt"] == "no" else "Only Additive Obs"
    ax.set_xlabel(r"Feels Like $^\circ$F, " f"{_tt}")
    ax.set_ylabel("Frequency [%]")
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_title(ctx["title"])

    # Clip the plot in the case of wind chill
    if ctx["var"].startswith("chill"):
        vals = non[non < 100]
        if len(vals.index) > 0:
            ax.set_xlim(right=vals.index.values[-1] + 2)

    return fig, ctx["df"]
