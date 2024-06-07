"""
This autoplot presents the total number of text products issued by UTC
month and year.

<p><a href="?q=210">Autoplot 210</a> presents a map of issuance counts
for all Weather Forecast Offices.</p>
"""

import calendar

import numpy as np
import pandas as pd
import seaborn as sns
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.reference import prodDefinitions
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network=["WFO", "NCEP", "RFC", "NWS"],
            default="DMX",
            label="Select Issuance Center:",
            all=True,
        ),
        dict(
            type="select",
            name="pil",
            default="AFD",
            label="Select 3 Character Product ID (AWIPS ID / AFOS)",
            options=prodDefinitions,
            showvalue=True,
        ),
        dict(type="cmap", name="cmap", default="Greens", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    pil = ctx["pil"]
    ctx["_nt"].sts["_ALL"] = {"name": "All Offices"}
    center = station
    if len(station) == 3:
        center = f"K{station}"

    params = {"center": center, "pil": pil}
    wfo_limiter = " and source = :center "
    params["wfo"] = station if len(station) == 3 else station[1:]
    if station == "_ALL":
        wfo_limiter = ""
        ctx["_sname"] = "All Offices"

    with get_sqlalchemy_conn("afos") as conn:
        ss = "pil = :pil" if len(pil) > 3 else "substr(pil, 1, 3) = :pil"
        df = pd.read_sql(
            text(
                f"""
                SELECT
                extract(year from entered at time zone 'UTC')::int as yr,
                extract(month from entered at time zone 'UTC')::int as mo,
                min(entered at time zone 'UTC') as min_entered,
                max(entered at time zone 'UTC') as max_entered,
                count(*)
                from products WHERE {ss} {wfo_limiter}
                GROUP by yr, mo ORDER by yr, mo ASC
        """
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

    title = f"NWS {ctx['_sname']} :: {prodDefinitions[pil]} [{pil}]"
    subtitle = (
        "Number of issued text products by year and month. "
        f"({df['min_entered'].min():%d %b %Y}-"
        f"{df['max_entered'].max():%d %b %Y})"
    )
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


if __name__ == "__main__":
    plotter({})
