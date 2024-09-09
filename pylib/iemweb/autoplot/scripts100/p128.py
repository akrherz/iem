"""
This chart compares yearly summaries between two long term climate sites. Only
years with similiar observation counts are used in this data presentation.
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context

from iemweb.autoplot.barchart import barchar_with_top10

PDICT = {
    "avg_high": "Average High Temperature",
    "avg_low": "Average Low Temperature",
    "avg_temp": "Average Temperature",
    "max_high": "Maximum Daily High",
    "min_high": "Minimum Daily High",
    "max_low": "Maximum Daily Low",
    "min_low": "Minimum Daily Low",
    "total_precip": "Total Precipitation",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT,
            name="var",
            label="Select Variable to Plot",
            default="avg_temp",
        ),
        dict(
            type="station",
            name="station1",
            default="IATDSM",
            label="Select First Station:",
            network="IACLIMATE",
        ),
        dict(
            type="station",
            name="station2",
            default="IATAME",
            label="Select Secont Station:",
            network="IACLIMATE",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx["station1"].upper()
    station2 = ctx["station2"].upper()
    varname = ctx["var"]

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """WITH one as (
        SELECT year, sum(precip) as one_total_precip,
        avg(high) as one_avg_high, avg(low) as one_avg_low,
        avg((high+low)/2.) as one_avg_temp,
        max(high) as one_max_high,
        min(high) as one_min_high,
        min(low) as one_min_low,
        max(low) as one_max_low, count(*) as obs from alldata WHERE
        station = %s GROUP by year),
        two as (
        SELECT year, sum(precip) as two_total_precip,
        avg(high) as two_avg_high, avg(low) as two_avg_low,
        avg((high+low)/2.) as two_avg_temp,
        max(high) as two_max_high,
        min(high) as two_min_high,
        min(low) as two_min_low,
        max(low) as two_max_low, count(*) as obs from alldata WHERE
        station = %s GROUP by year
        )

        SELECT o.year, one_total_precip, one_avg_high, one_avg_low,
        one_avg_temp, one_max_high, one_min_low, one_min_high, one_max_low,
        two_total_precip, two_avg_high,
        two_avg_low, two_avg_temp, two_max_high, two_min_low, two_min_high,
        two_max_low from one o, two t
        WHERE o.year = t.year and abs(o.obs - t.obs) < 5 ORDER by o.year ASC
        """,
            conn,
            params=(station1, station2),
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["one_station"] = station1
    df["two_station"] = station2
    for col in PDICT:
        df["diff_" + col] = df["one_" + col] - df["two_" + col]

    title = f"Yearly {PDICT[varname]} Difference"
    subtitle = (
        f"[{station1}] {ctx['_nt1'].sts[station1]['name']} minus "
        f"[{station2}] {ctx['_nt2'].sts[station2]['name']}"
    )
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    color_above = "b" if varname in ["total_precip"] else "r"
    color_below = "r" if color_above == "b" else "b"
    df["color"] = color_above
    df.loc[df[f"diff_{varname}"] < 0, "color"] = color_below

    ax = barchar_with_top10(
        fig,
        df,
        f"diff_{varname}",
        color=df["color"],
        table_col_title="Diff",
        labelformat="%.2f" if varname in ["total_precip"] else "%.1f",
    )

    units = "inch" if varname in ["total_precip"] else "F"
    lbl = "wetter" if units == "inch" else "warmer"
    wins = len(df[df["diff_" + varname] > 0].index)
    ax.text(
        0.5,
        0.95,
        "%s %s (%s/%s)"
        % (ctx["_nt1"].sts[station1]["name"], lbl, wins, len(df.index)),
        transform=ax.transAxes,
        ha="center",
    )
    wins = len(df[df["diff_" + varname] < 0].index)
    ax.text(
        0.5,
        0.05,
        "%s %s (%s/%s)"
        % (ctx["_nt2"].sts[station2]["name"], lbl, wins, len(df.index)),
        transform=ax.transAxes,
        ha="center",
    )
    ax.axhline(df["diff_" + varname].mean(), lw=2, color="k")
    ax.set_ylabel(
        "%s [%s] Avg: %.2f"
        % (PDICT[varname], units, df["diff_" + varname].mean())
    )
    ax.grid(True)
    ax.set_xlim(df.index.min() - 1, df.index.max() + 1)
    ymax = df["diff_" + varname].abs().max() * 1.1
    ax.set_ylim(0 - ymax, ymax)
    return fig, df
