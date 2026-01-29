"""
This chart presents a heatmap of the issuance hour of a given NWS Text
Product.  While data does exist back into the 1980s, the archive quality
and numerous changes with various products make long term plots a bit
problematic.  Please do not conflate this plot to represent when the given
products are active.  For example, a Flash Flood Watch issued at 9 AM and
valid for a period from 3 PM till 3 PM the next day will only count as one
at 9 AM.  If you want statistics on when various alerts are active, try
<a href="/plotting/auto/?p=48">Autoplot 48</a>.
"""

from datetime import date, datetime

import numpy as np
import pandas as pd
import seaborn as sns
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.reference import prodDefinitions
from sqlalchemy.engine import Connection

from iemweb.mlib import rectify_wfo

PDICT = {
    "utc": "UTC",
    "local": "Local Time for Forecast Office",
}
PDICT2 = {
    "single": "Single Product",
    "c1": "Combined (SVR + TOR + SVS + FFW + FFS)",
    "c2": "Combined (SVR + TOR)",
    "c3": "Combined (SVR + TOR + SVS)",
}
LOOKUP = {
    "c1": ["SVR", "TOR", "SVS", "FFW", "FFS"],
    "c2": ["SVR", "TOR"],
    "c3": ["SVR", "TOR", "SVS"],
}


def ensure_prodDefinitions_keys_in_labels():
    """
    Ensure each prodDefinitions label includes its key for clarity in UI.
    If the label does not already start with '[', prepend '[key] ' to it.
    This helps users distinguish similar product names in dropdowns.
    """
    for key, val in prodDefinitions.items():
        if not val.startswith("["):
            prodDefinitions[key] = f"[{key}] {val}"


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    ensure_prodDefinitions_keys_in_labels()
    desc["arguments"] = [
        dict(
            type="select",
            name="tzwhich",
            default="local",
            options=PDICT,
            label="Which timezone to use for summary?",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        {
            "type": "select",
            "name": "agg",
            "default": "single",
            "label": "Plot single product or given combination:",
            "options": PDICT2,
        },
        {
            "type": "select",
            "name": "pil",
            "default": "SVR",
            "label": "Select 3 Character Product Identifier (PIL):",
            "options": prodDefinitions,
        },
        {
            "type": "year",
            "min": 1980,
            "max": date.today().year,
            "name": "syear",
            "default": 2002,
            "label": "Inclusive Start Year for Summary",
        },
        {
            "type": "year",
            "min": 1980,
            "max": date.today().year,
            "name": "eyear",
            "default": date.today().year,
            "label": "Inclusive End Year for Summary",
        },
        {
            "type": "cmap",
            "name": "cmap",
            "default": "jet",
            "label": "Color Ramp",
        },
    ]
    return desc


@with_sqlalchemy_conn("afos")
def plotter(ctx: dict, conn: Connection | None = None):
    """Go"""
    wfo = ctx["wfo"]
    tzname = (
        "UTC" if ctx["tzwhich"] == "utc" else ctx["_nt"].sts[wfo]["tzname"]
    )

    params = {
        "source": rectify_wfo(wfo),
        "sts": date(ctx["syear"], 1, 1),
        "ets": date(ctx["eyear"], 12, 31),
        "tzname": tzname,
        "pils": LOOKUP.get(
            ctx["agg"],
            [
                ctx["pil"],
            ],
        ),
    }
    countsdf = pd.read_sql(
        sql_helper(
            """
    select extract(week from entered) as week,
    extract(hour from entered at time zone :tzname) as hour,
    count(*) from products where substr(pil, 1, 3) = ANY(:pils) and
    source = :source and entered >= :sts and entered <= :ets
    group by week, hour order by week, hour
    """
        ),
        conn,
        params=params,
        index_col=None,
    )
    if countsdf.empty:
        raise NoDataFound(
            f"No data found for {params['source']} {params['pils']} "
            f"between {params['sts']} and {params['ets']}"
        )
    # Reindex the DataFrame to fill out zeros
    countsdf = countsdf.pivot(
        index="hour", columns="week", values="count"
    ).reindex(range(24), columns=range(1, 54), fill_value=np.nan)

    label = (
        prodDefinitions[ctx["pil"]]
        if ctx["agg"] == "single"
        else PDICT2[ctx["agg"]]
    )
    title = f"Frequency of NWS {ctx['_nt'].sts[wfo]['name']} issued {label}"
    subtitle = (
        f"{params['sts']} to {params['ets']} in timezone {params['tzname']}"
    )

    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    # Add sums to RHS
    sumdf = countsdf.sum(axis="columns").fillna(0)
    for hour, count in sumdf.items():
        ax.text(54, hour + 0.5, f"{count:.0f}", va="center")
    sns.heatmap(
        countsdf,
        annot=False,
        linewidths=0.5,
        ax=ax,
        vmin=1,
        cmap=ctx["cmap"],
        zorder=2,
        square=False,
    )

    # Fix the y-axis tick rotation angle
    ax.tick_params(axis="y", rotation=0)
    ax.tick_params(axis="x", rotation=0)
    ax.set_ylim(0, 24)
    ax.set_xlim(0.5, 56.5)
    # Pretty up the y-axis label to be 0-12 AM/PM or 0-23 for UTC
    if params["tzname"] == "UTC":
        ax.set_yticks(np.arange(24) + 0.5)
    else:
        ax.set_yticks(np.arange(0, 24, 2) + 0.5)
        yticklabels = []
        for hr in range(0, 24, 2):
            dt = datetime(2000, 1, 1, hr)
            yticklabels.append(f"{dt:%-I %p}")
        ax.set_yticklabels(yticklabels)

    ax.set_xlabel("Week of Year")
    # Pretty up the x-axis labels
    xticks = []
    for month in range(2, 13):
        dt = datetime(2000, month, 1)
        xticks.append(dt.isocalendar()[1])
        ax.axvline(
            x=dt.isocalendar()[1],
            color="k",
            lw=0.5,
            zorder=3,
        )
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        [datetime(2000, month, 1).strftime("%b") for month in range(2, 13)]
    )

    ax.set_ylabel(f"Hour (Timezone: {params['tzname']})")

    return fig, countsdf
