"""
This chart displays the relative frequency of
VTEC products.  This is computed by taking the unique combination of
events and UGC county/zones.  Restating and for example, a single
Severe Thunderstorm Warning covering portions of two counties would
count as two events in this summary. The values plotted are relative to the
most frequent product.
"""

from datetime import date

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure_axes


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(
            type="year",
            name="syear",
            default=2009,
            label="Start Year (inclusive):",
            min=2009,
        ),
        dict(
            type="year",
            name="eyear",
            default=date.today().year,
            label="End Year (inclusive):",
            min=2009,
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    ctx["_nt"].sts["_ALL"] = dict(name="ALL WFOs")
    syear = ctx["syear"]
    eyear = ctx["eyear"] + 1
    station = ctx["station"][:4]
    sts = date(syear, 1, 1)
    ets = date(eyear, 1, 1)
    params = {
        "sts": sts,
        "ets": ets,
        "wfo": station if len(station) == 3 else station[1:5],
    }
    wfo_limiter = " and wfo = :wfo "
    if station == "_ALL":
        wfo_limiter = ""

    labels = []
    vals = []
    cnt = 1
    rows = []
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper(
                """
            select phenomena, significance, min(issue), count(*) from warnings
            where ugc is not null and issue > :sts
            and issue < :ets {wfo_limiter}
            GROUP by phenomena, significance ORDER by count DESC
        """,
                wfo_limiter=wfo_limiter,
            ),
            params,
        )
        if res.rowcount == 0:
            raise NoDataFound("No data found.")
        for row in res:
            label = (
                f"{cnt}. "
                f"{vtec.get_ps_string(row[0], row[1])} ({row[0]}.{row[1]})"
            )
            if cnt < 26:
                labels.append(label)
                vals.append(row[3])
            rows.append(
                dict(
                    phenomena=row[0],
                    significance=row[1],
                    count=row[3],
                    wfo=station,
                )
            )
            cnt += 1
    df = pd.DataFrame(rows)
    (fig, ax) = figure_axes(apctx=ctx)
    vals = np.array(vals)

    ax.barh(
        np.arange(len(vals)), vals / float(vals[0]) * 100.0, align="center"
    )
    for i in range(1, len(vals)):
        y = vals[i] / float(vals[0]) * 100.0
        ax.text(y + 1, i, f"{y:.1f}%", va="center")
    _tt = eyear - 1 if (eyear - 1 != syear) else ""
    fig.text(
        0.5,
        0.95,
        f"{syear}-{_tt} NWS {ctx['_sname']} Watch/Warning/Advisory Totals",
        ha="center",
    )
    fig.text(
        0.5,
        0.05,
        f"Event+County/Zone Count, Relative to #{labels[0]}",
        ha="center",
        fontsize=10,
    )
    ax.set_ylim(len(vals), -0.5)
    ax.grid(True)
    ax.set_yticklabels(labels)
    ax.set_yticks(np.arange(len(vals)))
    ax.set_position([0.5, 0.1, 0.45, 0.83])
    ax.set_xticks([0, 10, 25, 50, 75, 90, 100])

    return fig, df
