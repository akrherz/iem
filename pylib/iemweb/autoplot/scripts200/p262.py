"""
This autoplot lists out daily climate observation extremes for a given
combination of variable threshold and day offset.  For example, you can
ask for days with measurable snow cover, what was the top 10 warmest and
coldest high temperatures on the day following.

If the second variable picked is precip, snow, or snow depth, the lowest
15 values are not plotted as they are often zero and not as interesting
to look at.
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.reference import TRACE_VALUE

from iemweb.autoplot import ARG_STATION

PDICT = {
    "high": "High Temperature (°F)",
    "low": "Low Temperature (°F)",
    "precip": "Precipitation (inch)",
    "snow": "Snowfall (inch)",
    "snowd": "Snow Depth (inch)",
}


def format_value(varname, value):
    """Format values using precision appropriate for the selected variable."""
    if varname in ["high", "low"]:
        return f"{value:.0f}"
    if abs(value - TRACE_VALUE) < 1e-3:
        return "T"
    if varname == "precip":
        return f"{value:.2f}"
    return f"{value:.1f}"


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        {
            "type": "filtervar",
            "options": PDICT,
            "default": "snow",
            "comp_default": "ge",
            "t_default": 0.1,
            "name": "var1",
            "label": (
                "Select dataset filter requirement.  The IEM database "
                f"represents Trace values as {TRACE_VALUE}, so that is the "
                "threshold you would want to use to account for those values. "
            ),
        },
        {
            "type": "int",
            "ge": -365,
            "le": 365,
            "default": 1,
            "name": "offset",
            "label": (
                "Select number of days offset from the filtered events "
                "found with the previous setting (0 == same day):"
            ),
        },
        {
            "type": "select",
            "default": "high",
            "options": PDICT,
            "name": "var2",
            "label": "Variable after offset days to list top events for:",
        },
    ]
    return desc


def get_obsdf(ctx):
    """Figure out our observations."""
    comps = {
        "ge": ">=",
        "gt": ">",
        "le": "<=",
        "lt": "<",
        "eq": "==",
        "ne": "!=",
    }

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
    with first as (
        select day, {var1} as var1 from alldata where station = :station
        and {var1} is not null and {var1} {comp} :threshold
    ), second as (
        select day - '{offset} days'::interval as effective_day, day,
        {var2} as var2
        from alldata where station = :station and {var2} is not null
    )
    select f.day, f.var1, s.day as day2, s.var2 from first f JOIN second s
    on (f.day = s.effective_day) ORDER by s.var2 DESC
            """,
                var1=ctx["var1"],
                var2=ctx["var2"],
                offset=str(ctx["offset"]),
                comp=comps[ctx["var1_comp"]],
            ),
            conn,
            index_col="day",
            parse_dates=["day", "day2"],
            params={
                "station": ctx["station"],
                "threshold": ctx["var1_t"],
            },
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    return df


def make_table(ax, title, tabledf, var1: str, var2: str):
    """Render a compact table with consistent formatting."""
    ax.set_title(title, fontsize=13, loc="left")
    ax.axis("off")
    celltext = [
        [
            f"{day:%Y %b %d}",
            format_value(var1, row["var1"]),
            f"{row['day2']:%Y %b %d}",
            format_value(var2, row["var2"]),
        ]
        for day, row in tabledf.iterrows()
    ]
    table = ax.table(
        cellText=celltext,
        colLabels=[
            "Date",
            var1.capitalize(),
            "Second Date",
            var2.capitalize(),
        ],
        cellLoc="left",
        colLoc="left",
        bbox=[0, 0, 1, 0.97],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.25)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("0.8")
        if row == 0:
            cell.set_facecolor("#d9eaf4")
            cell.set_text_props(weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f6f6f6")
        else:
            cell.set_facecolor("white")
        if col in [1, 3]:
            cell._loc = "right"
    return table


def plotter(ctx: dict):
    """Go"""
    df = get_obsdf(ctx)

    fig = figure(
        title=(f"{ctx['_sname']}:: Top 15 Events for {PDICT[ctx['var2']]}"),
        subtitle=(
            f"on {ctx['offset']} day(s) from dates with {PDICT[ctx['var1']]} "
            f"{ctx['var1_comp']} {ctx['var1_t']}"
        ),
        apctx=ctx,
    )
    leftax = fig.add_axes((0.02, 0.09, 0.46, 0.76))
    make_table(
        leftax,
        "Top 15 Highest Values",
        df.head(15),
        ctx["var1"],
        ctx["var2"],
    )

    if ctx["var2"] not in ["precip", "snow", "snowd"]:
        rightax = fig.add_axes((0.52, 0.09, 0.46, 0.76))
        make_table(
            rightax,
            "Top 15 Lowest Values",
            df.sort_values("var2", ascending=True).head(15),
            ctx["var1"],
            ctx["var2"],
        )

    return fig, df
