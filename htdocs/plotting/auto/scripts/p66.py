"""Consec days"""
import calendar

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "above": "Temperature At or Above (AOA) Threshold",
    "below": "Temperature Below Threshold",
}
PDICT2 = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents the daily frequency of the
    given date having the prescribed number of previous days above or below
    some provided treshold. <a href="/plotting/auto/?q=216">Autoplot 216</a>
    provides actual streaks and yearly maximum values."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            options=PDICT2,
            label="Select which daily variable",
        ),
        dict(
            type="select",
            name="dir",
            default="above",
            options=PDICT,
            label="Select temperature direction",
        ),
        dict(
            type="int",
            name="threshold",
            default="60",
            label="Temperature Threshold (F):",
        ),
        dict(type="int", name="days", default="7", label="Number of Days:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    mydir = ctx["dir"]

    agg = "min" if mydir == "above" else "max"
    op = ">=" if mydir == "above" else "<"
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
            with data as (
                select day, {agg}({varname})
                OVER (ORDER by day ASC ROWS BETWEEN %s PRECEDING
                and CURRENT ROW) as agg from alldata_{station[:2]}
                where station = %s)

            select extract(doy from day) as doy,
            sum(case when agg {op} %s then 1 else 0 end)
                / count(*)::float * 100. as freq
            from data GROUP by doy ORDER by doy asc
        """,
            conn,
            params=(days - 1, station, threshold),
            index_col="doy",
        )

    label = "AOA" if mydir == "above" else "below"
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}\n"
        f"Frequency of {days} Consec Days with {varname.capitalize()} "
        f"{label} {threshold}"
        r"$^\circ$F "
    )
    fig, ax = figure_axes(apctx=ctx, title=title)
    ax.set_ylabel("Frequency of Days [%]")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.grid(True)
    ax.bar(df.index.values, df["freq"], width=1)

    ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)
    return fig, df


if __name__ == "__main__":
    plotter({})
