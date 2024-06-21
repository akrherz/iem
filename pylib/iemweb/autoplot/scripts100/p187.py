"""
This chart presents the rank a station's yearly
summary value has against an unweighted population of available
observations in the state.  The green line is a simple average of the
plot.
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context

from iemweb.autoplot.barchart import barchar_with_top10

PDICT = {
    "precip": "Total Precipitation",
    "high": "Average High Temperature",
    "low": "Average Low Temperature",
    "temp": "Average Temperature",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": True, "description": __doc__}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="var",
            default="precip",
            label="Variable to Plot:",
            options=PDICT,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    varname = ctx["var"]
    assert varname in PDICT
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        with data as (
            select station, year, sum(precip) as precip,
            avg(high) as high, avg(low) as low,
            avg((high+low)/2.) as temp, count(*) from alldata_{station[:2]}
            WHERE year >= 1893 GROUP by station, year
        ), counts as (
            select year, max(count) as maxcnt from data GROUP by year
        ), quorum as (
            select d.* from data d JOIN counts a on (d.year = a.year) WHERE
            d.count = a.maxcnt
        ), stdata as (
            select year, precip, high, low, temp from data where station = %s
        ), agg as (
            select station, year,
            avg({varname}) OVER (PARTITION by year) as avgval,
            rank() OVER (PARTITION by year ORDER by {varname} ASC) /
            count(*) OVER (PARTITION by year)::float * 100. as percentile
            from data)
        select a.station, a.year, a.percentile, s.{varname}, a.avgval
        from agg a JOIN stdata s on (a.year = s.year)
        where a.station = %s ORDER by a.year ASC
        """,
            conn,
            params=(station, station),
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    fig = figure(
        title=ctx["_sname"],
        subtitle=(
            f"Yearly {PDICT[varname]} Percentile for all "
            f"{station[:2]} stations"
        ),
        apctx=ctx,
    )
    overcolor = "b" if varname == "precip" else "r"
    undercolor = "r" if varname == "precip" else "b"
    df["color"] = overcolor
    df.loc[df["percentile"] < 50, "color"] = undercolor
    ax = barchar_with_top10(
        fig,
        df,
        "percentile",
        color=df["color"].tolist(),
    )
    current_pos = ax.get_position()
    ax.set_position([current_pos.x0, 0.5, current_pos.width, 0.4])
    meanval = df["percentile"].mean()
    ax.axhline(meanval, color="green", lw=2, zorder=5)
    ax.text(df.index.max() + 1, meanval, f"{meanval:.1f}", color="green")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax.set_ylabel("Percentile (no spatial weighting)")
    ax.grid(True)

    # second plot
    ax = fig.add_axes([current_pos.x0, 0.1, current_pos.width, 0.35])
    ax.bar(df.index.values, df[varname] - df["avgval"])
    meanval = (df[varname] - df["avgval"]).mean()
    ax.axhline(meanval, color="green", lw=2, zorder=5)
    ax.text(df.index.max() + 1, meanval, f"{meanval:.2f}", color="green")
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax.set_ylabel("Bias to State Arithmetic Mean")
    ax.grid(True)

    return fig, df
