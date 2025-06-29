"""
The NWS issues Special Weather Statements (SPS) products that often cover
events that are just below severe limits and/or not covered by other
headline products.  Sometimes these SPS products have polygons.  This
app provides a monthly total of the number of such SPS products.
"""

import calendar

import numpy as np
import pandas as pd
import seaborn as sns
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.reference import state_names

PDICT = {
    "wfo": "Select by NWS Forecast Office",
    "state": "Select by State",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT,
            label="How to summarize the data?",
        ),
        {
            "type": "state",
            "name": "state",
            "default": "IA",
            "label": "Select State:",
        },
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(type="cmap", name="cmap", default="Greens", label="Color Ramp:"),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}

    params = {}
    limiter = " and wfo = :wfo "
    params["wfo"] = station if len(station) == 3 else station[1:]
    if station == "_ALL":
        limiter = ""
        ctx["_sname"] = "All Offices"
    geo_table = ""
    title = f"NWS {ctx['_sname']} :: Polygon Special Weather Statements"
    if ctx["opt"] == "state":
        geo_table = ", states t"
        limiter = (
            " and ST_Intersects(t.the_geom, s.geom) and t.state_abbr = :state "
        )
        params["state"] = ctx["state"]
        title = (
            "NWS Polygon Special Weather Statements intersecting "
            f"{state_names[ctx['state']]} "
        )

    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper(
                """
                SELECT
                extract(year from issue)::int as yr,
                extract(month from issue)::int as mo, count(*)
                from sps s {geo_table} WHERE not ST_IsEmpty(geom) {limiter}
                GROUP by yr, mo ORDER by yr, mo ASC
        """,
                limiter=limiter,
                geo_table=geo_table,
            ),
            conn,
            params=params,
            index_col=None,
        )

    if df.empty:
        raise NoDataFound("Sorry, no data found!")

    df2 = df.pivot(index="yr", columns="mo", values="count").reindex(
        index=range(df["yr"].min(), df["yr"].max() + 1),
        columns=range(1, 13),
    )

    subtitle = "Number of issued products by year and month."
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    sns.heatmap(
        df2,
        annot=True,
        fmt=".0f",
        linewidths=0.5,
        ax=ax,
        vmin=1,
        cmap=ctx["cmap"],
        zorder=2,
    )
    # Add sums to RHS
    sumdf = df2.sum(axis="columns").fillna(0)
    for year, count in sumdf.items():
        ax.text(12, year, f"{count:.0f}")
    # Add some horizontal lines
    for i, year in enumerate(range(df["yr"].min(), df["yr"].max() + 1)):
        ax.text(
            12 + 0.7, i + 0.5, f"{sumdf[year]:4.0f}", ha="right", va="center"
        )
        if year % 5 != 0:
            continue
        ax.axhline(i, zorder=3, lw=1, color="gray")
    ax.text(1.0, -0.02, "Total", transform=ax.transAxes)
    # Add some vertical lines
    for i in range(1, 12):
        ax.axvline(i, zorder=3, lw=1, color="gray")
    ax.set_xticks(np.arange(12) + 0.5)
    ax.set_xticklabels(calendar.month_abbr[1:], rotation=0)
    ax.set_ylabel("Year")
    ax.set_xlabel("Month")

    return fig, df
