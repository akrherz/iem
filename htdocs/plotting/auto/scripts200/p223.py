"""Divide up the observations into partitions."""
import calendar
import datetime

from pandas import read_sql
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconnstr

PDICT = {
    "month": "Grouped by Month",
    "season": "Grouped by Season",
}
PDICT2 = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "precip": "Precipitation",
}
PDICT3 = {
    "percent": "Express as Percentages",
    "days": "Express as Days/Year",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents the monthly/seasonal partition of how a daily
    observed climate variable is observed.  Rewording, what percentage of
    a given year's daily reports at the given threshold range occur within
    the given month and season."""
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
            name="w",
            default="month",
            options=PDICT,
            label="How to group data",
        ),
        dict(
            type="select",
            name="how",
            default="percent",
            options=PDICT3,
            label="How to express data",
        ),
        dict(
            type="year",
            name="syear",
            default=1893,
            label="Inclusive Starting Year:",
        ),
        dict(
            type="year",
            name="eyear",
            default=datetime.date.today().year,
            label="Inclusive Ending Year:",
        ),
        dict(
            type="text",
            name="rng",
            default="70-79",
            label="Inclusive (both sides) range of values (F or inch)",
        ),
        dict(
            name="ymax",
            optional=True,
            type="float",
            default=5,
            label="Y-Axis Maximum Value (optional)",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    low, high = [float(x) for x in ctx["rng"].split("-")]
    varname = ctx["var"]

    df = read_sql(
        f"""
        select month,
        sum(case when {varname} >= %s and {varname} <= %s then 1 else 0 end)
        as hits, count(*)
        from alldata_{station[:2]} where station = %s and {varname} is not null
        and year >= %s and year <= %s GROUP by month ORDER by month ASC
    """,
        get_dbconnstr("coop"),
        params=(
            low,
            high,
            station,
            ctx["syear"],
            ctx["eyear"],
        ),
        index_col="month",
    )
    if df.empty:
        raise NoDataFound("Did not find any observations for station.")

    hits = df["hits"].sum()
    count = df["count"].sum()
    freq = hits / float(count) * 100.0
    days_per_year = freq / 100.0 * 365.0
    u = "inch" if varname == "precip" else "F"
    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}:: "
        f"Daily {PDICT2[varname]} between {low} and {high} {u} (inclusive)\n"
        f"Partition of Observed ({hits}/{count} {freq:.1f}%) "
        f"Days {PDICT[ctx['w']]} ({ctx['syear']}-{ctx['eyear']})"
    )

    fig, ax = figure_axes(title=title, apctx=ctx)
    if ctx["how"] == "percent":
        col = "freq"
        yunit = "%"
    else:
        col = "days"
        yunit = "days"
    ax.set_ylabel(f"Frequency [{yunit}]")
    ax.grid(True)
    if ctx["w"] == "month":
        df["freq"] = df["hits"] / df["hits"].sum() * 100.0
        df["days"] = df["freq"] / 100 * days_per_year
        bars = ax.bar(df.index.values, df[col].values, width=0.8)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(calendar.month_abbr[1:])
    else:
        df["season"] = "winter (DJF)"
        df.loc[df.index.isin([3, 4, 5]), "season"] = "spring (MAM)"
        df.loc[df.index.isin([6, 7, 8]), "season"] = "summer (JJA)"
        df.loc[df.index.isin([9, 10, 11]), "season"] = "fall (SON)"
        gdf = df.groupby("season").sum().copy()
        gdf["freq"] = gdf["hits"] / gdf["hits"].sum() * 100
        gdf["days"] = gdf["freq"] / 100 * days_per_year
        bars = ax.bar(
            range(1, 5),
            [
                gdf.at["winter (DJF)", col],
                gdf.at["spring (MAM)", col],
                gdf.at["summer (JJA)", col],
                gdf.at["fall (SON)", col],
            ],
            align="center",
        )
        ax.set_xticks(range(1, 5))
        ax.set_xticklabels(
            ["Winter (DJF)", "Spring (MAM)", "Summer (JJA)", "Fall (SON)"]
        )
    dy = ax.get_ylim()[1] - ax.get_ylim()[0]
    for bb in bars:
        ax.text(
            bb.get_x() + 0.4,
            bb.get_height() + dy * 0.05,
            f"{bb.get_height():.1f}{yunit[0]}",
            ha="center",
            fontsize=16,
            bbox=dict(color="white"),
        )
    ax.set_ylim(0, ctx.get("ymax", ax.get_ylim()[1] * 1.1))
    ax.set_xlabel(f"Average {(days_per_year):.1f} Days per Year")

    return fig, df


if __name__ == "__main__":
    plotter({"w": "season"})
