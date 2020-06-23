"""Extreme period each year"""
import datetime
from collections import OrderedDict

import numpy as np
from pandas.io.sql import read_sql
import matplotlib.colors as mpcolors
from matplotlib.colorbar import ColorbarBase
from matplotlib.ticker import MaxNLocator
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("coldest_temp", "Coldest Average Temperature"),
        ("coldest_hitemp", "Coldest Average High Temperature"),
        ("coldest_lotemp", "Coldest Average Low Temperature"),
        ("warmest_temp", "Warmest Average Temperature"),
        ("warmest_hitemp", "Warmest Average High Temperature"),
        ("warmest_lotemp", "Warmest Average Low Temperature"),
        ("wettest", "Highest Precipitation"),
    ]
)
# How to get plot variable from dataframe
XREF = {
    "coldest_temp": "avg_temp",
    "coldest_hitemp": "avg_hitemp",
    "coldest_lotemp": "avg_lotemp",
    "warmest_temp": "avg_temp",
    "warmest_hitemp": "avg_hitemp",
    "warmest_lotemp": "avg_lotemp",
    "wettest": "sum_precip",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot displays the period of consecutive days
    each year with the extreme criterion meet. In the case of a tie, the
    first period of the season is used for the analysis.
    """
    desc["arguments"] = [
        dict(
            type="sid",
            name="station",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="coldest_temp",
            label="Which Metric",
            options=PDICT,
        ),
        dict(type="int", name="days", default=7, label="Over How Many Days?"),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def get_data(ctx):
    """ Get the data"""
    days = ctx["days"]
    varname = ctx["var"]
    offset = 6 if varname.startswith("coldest") else 0
    station = ctx["station"]
    if ctx["network"].endswith("CLIMATE"):
        table = "alldata_%s" % (station[:2],)
        pgconn = get_dbconn("coop")
        highcol = "high"
        lowcol = "low"
        precipcol = "precip"
        stationcol = "station"
    else:
        station = ctx["_nt"].sts[station]["iemid"]
        pgconn = get_dbconn("iem")
        highcol = "max_tmpf"
        lowcol = "min_tmpf"
        precipcol = "pday"
        table = "summary"
        stationcol = "iemid"
    df = read_sql(
        f"""
    WITH data as (
    SELECT day, extract(year from day + '%s months'::interval) as season,
    avg(({highcol} + {lowcol})/2.)
        OVER (ORDER by day ASC ROWS %s preceding) as avg_temp,
    avg({highcol})
        OVER (ORDER by day ASC ROWS %s preceding) as avg_hitemp,
    avg({lowcol})
        OVER (ORDER by day ASC ROWS %s preceding) as avg_lotemp,
    sum({precipcol})
        OVER (ORDER by day ASC ROWS %s preceding) as sum_precip
    from {table} WHERE {stationcol} = %s and {highcol} is not null),
    agg1 as (
        SELECT season, day, avg_temp, avg_hitemp, avg_lotemp,
        sum_precip,
        rank() OVER (PARTITION by season ORDER by avg_temp ASC)
            as coldest_temp_rank,
        rank() OVER (PARTITION by season ORDER by avg_hitemp ASC)
            as coldest_hitemp_rank,
        rank() OVER (PARTITION by season ORDER by avg_lotemp ASC)
            as coldest_lotemp_rank,
        rank() OVER (PARTITION by season ORDER by avg_temp DESC)
            as warmest_temp_rank,
        rank() OVER (PARTITION by season ORDER by avg_hitemp DESC)
            as warmest_hitemp_rank,
        rank() OVER (PARTITION by season ORDER by avg_lotemp DESC)
            as warmest_lotemp_rank,
        rank() OVER (PARTITION by season ORDER by sum_precip DESC)
            as wettest_rank,
        count(*) OVER (PARTITION by season)
        from data)
    SELECT season, day,
    extract(doy from day - '%s days'::interval)::int as doy,
    avg_temp, avg_hitemp, avg_lotemp,
    sum_precip from agg1 where {varname}_rank = 1 and count > 240
    """,
        pgconn,
        params=(
            offset,
            days - 1,
            days - 1,
            days - 1,
            days - 1,
            station,
            days - 1,
        ),
        index_col="season",
    )
    if varname.startswith("coldest"):
        df.loc[df["doy"] < 183, "doy"] += 365.0
    return df


def plotter(fdict):
    """ Go """
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = ctx["days"]
    varname = ctx["var"]
    df = get_data(ctx)
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_axes([0.1, 0.3, 0.75, 0.6])
    lax = fig.add_axes([0.1, 0.1, 0.75, 0.2])
    cax = fig.add_axes([0.87, 0.3, 0.03, 0.6])
    title = PDICT.get(varname)
    if days == 1:
        title = title.replace("Average ", "")
    ax.set_title(
        ("%s [%s]\n%i Day Period with %s")
        % (ctx["_nt"].sts[station]["name"], station, days, title)
    )
    cmap = plt.get_cmap(ctx["cmap"])
    minval = df[XREF[varname]].min() - 1.0
    if varname == "wettest" and minval < 0:
        minval = 0
    maxval = df[XREF[varname]].max() + 1.0
    ramp = np.linspace(
        minval, maxval, min([int(maxval - minval), 10]), dtype="i"
    )
    norm = mpcolors.BoundaryNorm(ramp, cmap.N)
    cb = ColorbarBase(cax, norm=norm, cmap=cmap)
    cb.set_label("inch" if varname == "wettest" else r"$^\circ$F")
    ax.barh(
        df.index.values,
        [days] * len(df.index),
        left=df["doy"].values,
        color=cmap(norm(df[XREF[varname]].values)),
    )
    ax.grid(True)
    lax.grid(True)
    xticks = []
    xticklabels = []
    for i in np.arange(df["doy"].min() - 5, df["doy"].max() + 5, 1):
        ts = datetime.datetime(2000, 1, 1) + datetime.timedelta(days=int(i))
        if ts.day == 1:
            xticks.append(i)
            xticklabels.append(ts.strftime("%-d %b"))
    ax.set_xticks(xticks)
    lax.set_xticks(xticks)
    lax.set_xticklabels(xticklabels)

    counts = np.zeros(366 * 2)
    for _, row in df.iterrows():
        counts[int(row["doy"]) : int(row["doy"] + days)] += 1

    lax.bar(np.arange(366 * 2), counts, edgecolor="blue", facecolor="blue")
    lax.set_ylabel("Years")
    lax.text(
        0.02,
        0.9,
        "Frequency of Day\nwithin period",
        transform=lax.transAxes,
        va="top",
    )
    ax.set_ylim(df.index.values.min() - 3, df.index.values.max() + 3)

    ax.set_xlim(df["doy"].min() - 10, df["doy"].max() + 10)
    lax.set_xlim(df["doy"].min() - 10, df["doy"].max() + 10)
    ax.yaxis.set_major_locator(MaxNLocator(prune="lower"))
    return fig, df


if __name__ == "__main__":
    plotter(dict(station="IA0112", var="wettest", network="IACLIMATE", days=3))
