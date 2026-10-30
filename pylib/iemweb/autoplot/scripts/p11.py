"""
This plot presents the range between the min
and maximum observation of your choice for a given station and a given
year.  Some of these values are only computed based on hourly reports,
so they would be represent a true min and max of a continuously observed
variable.
"""

from datetime import datetime, timedelta
from typing import Annotated

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot.description import (
    IntArg,
    PlotDescription,
    SelectArg,
    YearArg,
    ZStationArg,
)
from iemweb.autoplot.params import AutoplotParams

PDICT = {
    "below": "Daily Range Below Emphasis",
    "atbelow": "Daily Range At or Below Emphasis",
    "touches": "Daily Range Touches Emphasis",
    "above": "Daily Range At or Above Emphasis",
}

PDICT2 = {
    "tmpf": "Air Temperature",
    "dwpf": "Dew Point Temperature",
    "feel": "Feels Like Temperature",
    "rh": "Relative Humidity",
}


class Params(AutoplotParams):
    """Request parameters."""

    zstation: Annotated[
        str, ZStationArg(label="Select Station:", network="IA_ASOS")
    ] = "AMW"
    year: Annotated[
        int,
        YearArg(
            min=1900, label="Select Year:", default=lambda: datetime.now().year
        ),
    ]
    emphasis: Annotated[
        int,
        IntArg(
            label="Temperature(°F) or RH(%) Line of Emphasis (-99 disables):"
        ),
    ] = -99
    var: Annotated[
        str, SelectArg(label="Which variable to plot?", options=PDICT2)
    ] = "dwpf"
    opt: Annotated[
        str, SelectArg(label="Option for Highlighting", options=PDICT)
    ] = "touches"


def get_description() -> PlotDescription:
    """Return a description of how to call this plotter."""
    return PlotDescription.from_model(
        Params, description=__doc__ or "", data=True
    )


def plotter(ctx: Params):
    """Go"""
    station = ctx.zstation
    year = ctx.year
    emphasis = ctx.emphasis
    opt = ctx.opt
    varname = ctx.var
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            select day, max_{varname}, min_{varname}
            from {table} s JOIN stations t on (s.iemid = t.iemid)
            where t.id = :station and t.network = :network and
            max_{varname} is not null and
            min_{varname} is not null
            ORDER by day ASC
        """,
                varname=varname,
                table=f"summary_{year}",
            ),
            conn,
            params={"station": station, "network": ctx["network"]},
            index_col="day",
        )
    if df.empty:
        raise NoDataFound("No Data Found!")
    df["range"] = df[f"max_{varname}"] - df[f"min_{varname}"]

    minval = df[f"min_{varname}"].min()
    maxval = df[f"max_{varname}"].max()
    title = (
        f"{ctx.sname}:: {year} "
        f"Daily Min/Max {PDICT2[varname]}\n"
        f"Period: {df.index.values[0]:%-d %B} to {df.index.values[-1]:%-d %B}"
        f" , Min: {minval:.0f} Max: {maxval:.0f}"
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes((0.1, 0.15, 0.8, 0.75))
    bars = ax.bar(
        df.index.values,
        df["range"].to_numpy(),
        ec="g",
        fc="g",
        bottom=df[f"min_{varname}"].values,
        zorder=1,
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d\n%b"))
    hits = []
    if emphasis > -99:
        for i, mybar in enumerate(bars):
            minval = mybar.get_y()
            maxval = mybar.get_y() + mybar.get_height()
            if (
                (maxval >= emphasis >= minval and opt == "touches")
                or (minval >= emphasis and opt == "above")
                or (maxval < emphasis and opt == "below")
                or (minval <= emphasis and opt == "atbelow")
            ):
                mybar.set_facecolor("r")
                mybar.set_edgecolor("r")
                hits.append(df.index.values[i])
        ax.axhline(emphasis, lw=2, color="k")
        ax.text(
            df.index.values[-1] + timedelta(days=2),
            emphasis,
            f"{emphasis}",
            ha="left",
            va="center",
        )
    ax.grid(True)
    ll = "°F" if varname != "rh" else "%"
    ax.set_ylabel(f"{PDICT2[varname]} {ll}")
    ax.set_xlabel(
        f"Days meeting emphasis: {len(hits)}, "
        f"first: {hits[0].strftime('%B %d') if hits else 'None'} "
        f"last: {hits[-1].strftime('%B %d') if hits else 'None'}"
    )
    delta = timedelta(days=1)
    ax.set_xlim(df.index.values[0] - delta, df.index.values[-1] + delta)
    return fig, df
