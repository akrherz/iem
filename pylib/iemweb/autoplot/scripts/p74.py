"""
The number of days for a given season that are
either above or below some temperature threshold.
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from scipy import stats

PDICT = {"above": "At or Above Threshold", "below": "Below Threshold"}
PDICT2 = {
    "winter": "Winter (Dec, Jan, Feb)",
    "spring": "Spring (Mar, Apr, May)",
    "summer": "Summer (Jun, Jul, Aug)",
    "fall": "Fall (Sep, Oct, Nov)",
    "all": "Entire Year",
}
PDICT3 = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="season",
            default="winter",
            label="Select Season:",
            options=PDICT2,
        ),
        dict(
            type="select",
            name="dir",
            default="below",
            label="Threshold Direction:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="var",
            default="low",
            label="Which Daily Variable:",
            options=PDICT3,
        ),
        dict(
            type="float",
            name="threshold",
            default=0,
            label="Temperature (F) or Precip (in) Threshold:",
        ),
        dict(
            type="year", name="year", default=1893, label="Start Year of Plot"
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    season = ctx["season"]
    direction = ctx["dir"]
    varname = ctx["var"]
    threshold = ctx["threshold"]
    startyear = ctx["year"]

    b = f"{varname} {'>=' if direction == 'above' else '<'} {threshold}"

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        SELECT extract(year from day + '%s month'::interval) as yr,
        sum(case when month in (12, 1, 2) and {b}
        then 1 else 0 end) as winter,
        sum(case when month in (3, 4, 5) and {b}
        then 1 else 0 end) as spring,
        sum(case when month in (6, 7, 8) and {b}
        then 1 else 0 end) as summer,
        sum(case when month in (9, 10, 11) and {b}
        then 1 else 0 end) as fall,
        sum(case when {b} then 1 else 0 end) as all
        from alldata WHERE station = %s and year >= %s
        GROUP by yr ORDER by yr ASC
        """,
            conn,
            params=(1 if season != "all" else 0, station, startyear),
            index_col="yr",
        )
    if df.empty:
        raise NoDataFound("No data found for query")

    tt = r"$^\circ$F" if varname != "precip" else "inch"
    title = (
        f"{ctx['_sname']} {df.index.min():.0f}-{df.index.max():.0f} "
        "Number of Days\n"
        f"[{PDICT2[season]}] with {PDICT3[varname]} {PDICT[direction]} "
        f"{threshold}{tt}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    avgv = df[season].mean()

    colorabove = "r"
    colorbelow = "b"
    if direction == "below":
        colorabove = "b"
        colorbelow = "r"
    bars = ax.bar(
        df.index.values,
        df[season],
        fc=colorabove,
        ec=colorabove,
        align="center",
    )
    for i, mybar in enumerate(bars):
        if df[season].values[i] < avgv:
            mybar.set_facecolor(colorbelow)
            mybar.set_edgecolor(colorbelow)
    ax.axhline(avgv, lw=2, color="k", zorder=2, label="Average")
    h_slope, intercept, r_value, _, _ = stats.linregress(
        df.index.values, df[season]
    )
    ax.plot(
        df.index.values,
        h_slope * df.index.values + intercept,
        "--",
        lw=2,
        color="k",
        label="Trend",
    )
    ax.text(
        0.01,
        0.99,
        f"Avg: {avgv:.1f}, slope: {h_slope * 100.:.2f} days/century, "
        f"R$^2$={r_value**2:.2f}",
        transform=ax.transAxes,
        va="top",
        bbox=dict(color="white"),
    )
    ax.set_xlabel("Year")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim(0, max([df[season].max() + df[season].max() / 7.0, 3]))
    ax.set_ylabel("Number of Days")
    ax.grid(True)
    ax.legend(ncol=1)

    return fig, df


if __name__ == "__main__":
    plotter({})
