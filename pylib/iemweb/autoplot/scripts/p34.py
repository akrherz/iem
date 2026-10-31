"""
This plot displays the maximum number of consec
days above or below some threshold for high or low temperature.
"""

import calendar
from datetime import date, datetime, timedelta
from typing import Annotated

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, fitbox

from iemweb.autoplot import ARG_STATION, get_monofont
from iemweb.autoplot.description import IntArg, PlotDescription, SelectArg
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "high_over": "High Temperature At or Above",
    "high_under": "High Temperature Below",
    "avgt_over": "Daily Average Temperature At or Above",
    "avgt_under": "Daily Average Temperature Below",
    "low_over": "Low Temperature At or Above",
    "low_under": "Low Temperature Below",
}
TDICT = {
    "threshold": "Compare against prescribed threshold",
    "average": "Compare against climatological average",
}
ADICT = {
    "por": "Period of Record",
    "1951": "1951-present",
    "ncei81": "NCEI 1981-2010 Climate Normals",
    "ncei91": "NCEI 1991-2020 Climate Normals",
}


class Params(AutoplotParams):
    """Request parameters."""

    station: Annotated[str, ARG_STATION] = "IATAME"
    var: Annotated[
        str, SelectArg(label="Which Streak to Compute:", options=PDICT)
    ] = "high_under"
    which: Annotated[
        str,
        SelectArg(options=TDICT, label="Which baseline to compare against?"),
    ] = "threshold"
    climo: Annotated[
        str,
        SelectArg(
            options=ADICT,
            label="For Climatology Comparison, which climatolog to use?",
        ),
    ] = "por"
    threshold: Annotated[int, IntArg(label="Temperature Threshold:")] = 32


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def greater_than_or_equal(one, two):
    """Helper."""
    return one >= two


def less_than(one, two):
    """Helper."""
    return one < two


def plotter(ctx: Params):
    """Go"""
    station = ctx.station
    threshold = ctx.threshold
    varname = ctx.var

    # Get averages
    if ctx.climo == "por":
        cltable = "climate"
        clstation = station
    elif ctx.climo == "1951":
        cltable = "climate51"
        clstation = station
    elif ctx.climo == "ncei81":
        cltable = "ncdc_climate81"
        clstation = ctx["_nt"].sts[station]["ncdc81"]
    else:  # ncei91
        cltable = "ncei_climate91"
        clstation = ctx["_nt"].sts[station]["ncei91"]
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            sql_helper(
                """
            WITH myclimo as (
                select to_char(valid, 'mmdd') as sday, high, low,
                (high + low) / 2. as avgt from
                {table} WHERE station = :clstation
            )
            SELECT extract(doy from day)::int as d, o.high, o.low, o.day,
            (o.high + o.low) / 2. as avgt,
            c.high as climo_high, c.low as climo_low, c.avgt as climo_avgt
            from alldata o JOIN myclimo c on (o.sday = c.sday)
            where o.station = :st and o.high is not null ORDER by day ASC
            """,
                table=cltable,
            ),
            conn,
            params={"clstation": clstation, "st": station},
            index_col="day",
        )
    if obs.empty:
        raise NoDataFound("No observations found for given station.")
    obs["threshold"] = threshold

    maxperiod = [0] * 367
    enddate = [""] * 367
    running = 0
    col = varname.replace("_over", "").replace("_under", "")
    myfunc = greater_than_or_equal if varname.find("over") > 0 else less_than
    compcol = "threshold"
    if ctx.which == "average":
        compcol = f"climo_{col}"
    streaks = []
    running = 0
    day = None
    for day, row in obs.iterrows():
        doy = int(row["d"])
        if myfunc(row[col], row[compcol]):
            running += 1
        else:
            if running > 0:
                streaks.append([running, day - timedelta(days=1)])
            running = 0
        if running > maxperiod[doy]:
            maxperiod[doy] = running
            enddate[doy] = str(day)
    if running > 0:
        streaks.append([running, day])

    sts = datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(ts.timetuple().tm_yday)

    sdf = pd.DataFrame(streaks, columns=["period", "enddate"])
    df = pd.DataFrame(
        dict(
            mmdd=pd.date_range("1/1/2000", "12/31/2000").strftime("%m%d"),
            jdate=pd.Series(np.arange(1, 367)),
            maxperiod=pd.Series(maxperiod[1:]),
            enddate=pd.Series(enddate[1:]),
        )
    )
    df["startdate"] = df["enddate"]
    fig = figure(apctx=ctx)
    ax = fig.add_axes((0.1, 0.1, 0.55, 0.8))
    ax.bar(np.arange(1, 367), maxperiod[1:], fc="b", ec="b")
    ax.grid(True)
    ax.set_ylabel("Consecutive Days")
    ttitle = f"{threshold}°F"
    if ctx.which == "average":
        ttitle = f"Average ({ADICT[ctx.climo]})"
    title = (
        f"{ctx.sname} ({obs.index[0]:%Y %b %d}-"
        f"{obs.index[-1]:%Y %b %d})\n"
        f"Maximum Straight Days with {PDICT[varname]} {ttitle}"
    )
    fitbox(fig, title, 0.1, 0.92, 0.9, 0.97)
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    # List top 20 periods
    ypos = 0.8
    fig.text(0.7, ypos, "Top 20 Distinct Periods\nDays - Inclusive Period")
    ypos -= 0.06
    monofont = get_monofont()
    today = date.today()
    for idx, row in (
        sdf.sort_values("period", ascending=False).head(20).iterrows()
    ):
        d2 = row["enddate"]
        d1 = d2 - timedelta(days=row["period"] - 1)
        df.loc[idx, "startdate"] = f"{d1:%Y-%m-%d}"
        fig.text(
            0.7,
            ypos,
            f"{row['period']} - {d1:%Y %b %d} -> {d2:%Y %b %d}",
            color="red" if d2.year == today.year else "k",
            fontproperties=monofont,
        )
        ypos -= 0.03
    fig.text(0.7, ypos, "* Overlapping Periods Not Listed")

    return fig, df
