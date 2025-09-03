"""
Based on hourly observations, this plot displays the frequency of a given
variable falling within a set of thresholds.  The thresholds are defined by
the user and must be in ascending order.  The plot is broken down by week
of the year.  There is an option to control how hours are handled that do
not have the given variable reported.  This gets thorny with non-continuously
monitored / reported variables like wind gust. If you turn that setting off,
the weekly totals will add to 100%, but you should not assume that all hours
are accounted for or that it represents a true frequency of time.
"""

import calendar
from datetime import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

PDICT = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "feel": "Feels Like Temperature",
    "sknt": "Wind Speed",
    "gust": "Wind Gust",
    "alti": "Pressure",
    "p01i": "Precipitation",
    "vsby": "Visibility",
    "mslp": "Mean Sea Level Pressure",
}
UNITS = {
    "tmpf": "°F",
    "dwpf": "°F",
    "feel": "°F",
    "sknt": "knots",
    "gust": "knots",
    "alti": "inches",
    "p01i": "inches",
    "vsby": "miles",
    "mslp": "millibars",
}
CAST = {
    "tmpf": "int",
    "dwpf": "int",
    "feel": "int",
}
MDICT = {
    "yes": "Yes, account for missing / no reports",
    "no": "No, ignore missing / no reports",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400, "data": True}
    tu = "[F, inch, %, knots, mb]"
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            options=PDICT,
            default="tmpf",
            name="var",
            label="Select variable to plot:",
        ),
        dict(
            type="int",
            name="t1",
            default=0,
            label=f"Threshold #1 (lowest) {tu}",
        ),
        dict(type="int", name="t2", default=32, label=f"Threshold #2 {tu}"),
        dict(type="int", name="t3", default=50, label=f"Threshold #3 {tu}"),
        dict(type="int", name="t4", default=70, label=f"Threshold #4 {tu}"),
        dict(
            type="int",
            name="t5",
            default=90,
            label=f"Threshold #5 (highest) {tu}",
        ),
        {
            "type": "select",
            "name": "missing",
            "default": "yes",
            "label": "Account for missing / no reports in totals?",
            "options": MDICT,
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    # Ensure that the thresholds are in order
    arr = [ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"], ctx["t5"]]
    arr.sort()
    if arr != [ctx["t1"], ctx["t2"], ctx["t3"], ctx["t4"], ctx["t5"]]:
        raise NoDataFound("Thresholds must be in ascending order")
    params = {
        "station": ctx["zstation"],
        "t1": ctx["t1"],
        "t2": ctx["t2"],
        "t3": ctx["t3"],
        "t4": ctx["t4"],
        "t5": ctx["t5"],
    }
    t1 = ctx["t1"]
    t2 = ctx["t2"]
    t3 = ctx["t3"]
    t4 = ctx["t4"]
    t5 = ctx["t5"]
    v = ctx["var"]
    cst = CAST.get(v, "float")
    mlim = f"and {v} is not null" if ctx["missing"] == "no" else ""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    SELECT extract(week from valid) as week,
    min(valid) as min_valid, max(valid) as max_valid,
    sum(case when {v}::{cst} < :t1 then 1 else 0 end) as d1,
    sum(case when {v}::{cst} < :t2 and {v}::{cst} >= :t1 then 1 else 0 end)
    as d2,
    sum(case when {v}::{cst} < :t3 and {v}::{cst} >= :t2 then 1 else 0 end)
    as d3,
    sum(case when {v}::{cst} < :t4 and {v}::{cst} >= :t3 then 1 else 0 end)
    as d4,
    sum(case when {v}::{cst} < :t5 and {v}::{cst} >= :t4 then 1 else 0 end)
    as d5,
    sum(case when {v}::{cst} >= :t5 then 1 else 0 end) as d6,
    sum(case when {v} is null then 1 else 0 end) as dnull,
    count(*)
    from alldata where station = :station and report_type = 3 {mlim}
    GROUP by week ORDER by week ASC
        """,
                v=v,
                cst=cst,
                mlim=mlim,
            ),
            conn,
            params=params,
            index_col="week",
        )
    if df.empty:
        raise NoDataFound("No observations found for query.")

    for i in range(1, 7):
        df[f"p{i}"] = df[f"d{i}"] / df["count"] * 100.0
    sts = datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(ts.timetuple().tm_yday / 7.0)

    title = f"Hourly {PDICT[v]} {UNITS[v]} Frequencies "
    subtitle = (
        f"{ctx['_sname']} "
        f"({df.iloc[0]['min_valid'].year}-{df.iloc[0]['max_valid'].year})"
    )
    if ctx["missing"] == "no":
        subtitle += " [Missing/No Report Hours Ignored]"
    (fig, ax) = figure_axes(apctx=ctx, title=title, subtitle=subtitle)
    x = df.index.values - 1
    if ctx["missing"] == "yes":
        val = df["dnull"].sum() / df["count"].sum() * 100.0
        ax.bar(
            x,
            df["dnull"].values,
            bottom=(
                df["p6"] + df["p5"] + df["p4"] + df["p3"] + df["p2"] + df["p1"]
            ).values,
            width=1,
            fc="white",
            ec="None",
            label=f"Missing/No Report ({val:.2f}%)",
        )
    val = df["d6"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p6"].values,
        bottom=(df["p5"] + df["p4"] + df["p3"] + df["p2"] + df["p1"]).values,
        width=1,
        fc="red",
        ec="None",
        label=f"Above {t5} ({val:.2f}%)",
    )
    val = df["d5"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p5"].values,
        bottom=(df["p4"] + df["p3"] + df["p2"] + df["p1"]).values,
        width=1,
        fc="tan",
        ec="None",
        label=f">={t4},<{t5} ({val:.2f}%)",
    )
    val = df["d4"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p4"].values,
        bottom=(df["p3"] + df["p2"] + df["p1"]).values,
        width=1,
        fc="yellow",
        ec="None",
        label=f">={t3},<{t4} ({val:.2f}%)",
    )
    val = df["d3"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p3"].values,
        width=1,
        fc="green",
        bottom=(df["p2"] + df["p1"]).values,
        ec="None",
        label=f">={t2},<{t3} ({val:.2f}%)",
    )
    val = df["d2"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p2"].values,
        bottom=df["p1"].values,
        width=1,
        fc="blue",
        ec="None",
        label=f">={t1},<{t2} ({val:.2f}%)",
    )
    val = df["d1"].sum() / df["count"].sum() * 100.0
    ax.bar(
        x,
        df["p1"].values,
        width=1,
        fc="purple",
        ec="None",
        label=f"Below {t1} ({val:.2f}%)",
    )

    ax.grid(True, zorder=11)
    ax.set_ylabel("Frequency [%]")

    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 53)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8]
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        shadow=True,
        ncol=3,
        scatterpoints=1,
        fontsize=12,
    )

    return fig, df
