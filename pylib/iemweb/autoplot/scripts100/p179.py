"""
This application creates two 2-D histograms of
GDD accumulation frequencies. These frequencies are based on historical
data for the specificed site and base the end of each year's growing
season on the first sub freezing temperature of the fall.  The left hand
plot shows the overall frequency based on each year's data.  The right
hand plot does a scenario using the combination of year to date data for
this year and then each previous year afterwards is appended to this
year's data to provide frequencies.  The right hand plot is meant to
provide current frequencies / probabilities of what could potentially
happen this year.
"""

import datetime as dt
from datetime import date, datetime
from typing import Annotated

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.plot import figure, get_cmap
from sqlalchemy.engine import Connection

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.description import (
    CmapArg,
    DateArg,
    IntArg,
    PlotDescription,
)
from iemweb.autoplot.params import AutoplotParams


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    gddbase: Annotated[
        int, IntArg(label="Growing Degree Days to Accumulate:")
    ] = 2300
    base: Annotated[int, IntArg(label="Growing Degree Day Base (F)")] = 50
    ceil: Annotated[int, IntArg(label="Growing Degree Day Ceiling (F)")] = 86
    date: Annotated[
        dt.date,
        DateArg(
            label="Retroactive Date:",
            min="1893/01/01",
            default=lambda: date.today().strftime("%Y/%m/%d"),
        ),
    ]
    cmap: Annotated[str, CmapArg(label="Color Ramp:")] = "jet"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


@with_sqlalchemy_conn("coop")
def plotter(ctx: Params, conn: Connection | None = None):
    """Go"""
    station = ctx.station
    gddbase = ctx.gddbase
    base = ctx.base
    ceil = ctx.ceil
    today: date = ctx.date
    bs = ctx["_nt"].sts[station]["archive_begin"]
    byear = bs.year
    eyear = today.year + 1
    res = conn.execute(
        sql_helper("""
        SELECT year, extract(doy from day), gddxx(:base, :ceil, high,low), low
        from alldata where station = :station and year > :byear and
        day < :today and high is not null and low is not null
        """),
        {
            "base": base,
            "ceil": ceil,
            "station": station,
            "byear": byear,
            "today": today,
        },
    )

    gdd = np.zeros((eyear - byear, 366), "f")
    freezes = np.zeros((eyear - byear), "f")
    freezes[:] = 400.0

    for row in res:
        gdd[int(row[0]) - byear, int(row[1]) - 1] = row[2]
        if row[1] > 180 and row[3] < 32 and row[1] < freezes[row[0] - byear]:
            freezes[int(row[0]) - byear] = row[1]

    for i, freeze in enumerate(freezes):
        gdd[i, int(freeze) :] = 0.0

    idx = today.timetuple().tm_yday - 1
    apr1 = datetime(2000, 4, 1).timetuple().tm_yday - 1
    jun30 = datetime(2000, 6, 30).timetuple().tm_yday - 1
    sep1 = datetime(2000, 9, 1).timetuple().tm_yday - 1
    oct31 = datetime(2000, 10, 31).timetuple().tm_yday - 1

    # Replace all years with the last year's data
    scenario_gdd = gdd * 1
    scenario_gdd[:-1, :idx] = gdd[-1, :idx]

    # store our probs
    probs = np.zeros((oct31 - sep1, jun30 - apr1), "f")
    scenario_probs = np.zeros((oct31 - sep1, jun30 - apr1), "f")

    rows = []
    for x in range(apr1, jun30):
        for y in range(sep1, oct31):
            sums = np.where(np.sum(gdd[:-1, x:y], 1) >= gddbase, 1, 0)
            probs[y - sep1, x - apr1] = sum(sums) / float(len(sums)) * 100.0
            sums = np.where(np.sum(scenario_gdd[:-1, x:y], 1) >= gddbase, 1, 0)
            scenario_probs[y - sep1, x - apr1] = (
                sum(sums) / float(len(sums)) * 100.0
            )
            rows.append(
                dict(
                    x=x,
                    y=y,
                    prob=probs[y - sep1, x - apr1],
                    scenario_probs=scenario_probs[y - sep1, x - apr1],
                )
            )
    df = pd.DataFrame(rows)

    probs = np.where(probs < 0.1, -1, probs)
    scenario_probs = np.where(scenario_probs < 0.1, -1, scenario_probs)
    title = (
        f"({byear}-{eyear - 1}) {ctx.sname}:: GDDs\n"
        f"Frequency [%] of reaching {gddbase:.0f} GDDs "
        f"({base:.0f}/{ceil:.0f}) prior to first freeze"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(1, 2, sharey=True)

    cmap = get_cmap(ctx.cmap).with_extremes(under="white")
    norm = mpcolors.BoundaryNorm(np.arange(0, 101, 5), cmap.N)

    ax[0].imshow(
        np.flipud(probs),
        aspect="auto",
        extent=[apr1, jun30, sep1, oct31],
        interpolation="nearest",
        cmap=cmap,
        norm=norm,
    )
    ax[0].grid(True)
    ax[0].set_title("Overall Frequencies")
    ax[0].set_xticks((91, 106, 121, 136, 152, 167))
    ax[0].set_ylabel("Growing Season End Date")
    ax[0].set_xlabel("Growing Season Begin Date")
    ax[0].set_xticklabels(("Apr 1", "15", "May 1", "15", "Jun 1", "15"))
    ax[0].set_yticks((244, 251, 258, 265, 274, 281, 288, 295, 305))
    ax[0].set_yticklabels(
        "Sep 1,Sep 8,Sep 15,Sep 22,Oct 1,Oct 8,Oct 15,Oct 22,Nov".split(",")
    )

    res = ax[1].imshow(
        np.flipud(scenario_probs),
        aspect="auto",
        extent=[apr1, jun30, sep1, oct31],
        interpolation="nearest",
        cmap=cmap,
        norm=norm,
    )
    ax[1].grid(True)
    ax[1].set_title(f"Scenario after {today:%-d %B %Y}")
    ax[1].set_xticks((91, 106, 121, 136, 152, 167))
    ax[1].set_xticklabels(("Apr 1", "15", "May 1", "15", "Jun 1", "15"))
    ax[1].set_xlabel("Growing Season Begin Date")

    fig.subplots_adjust(bottom=0.20, top=0.85)
    cbar_ax = fig.add_axes((0.05, 0.06, 0.85, 0.05))
    fig.colorbar(res, cax=cbar_ax, orientation="horizontal")

    return fig, df
