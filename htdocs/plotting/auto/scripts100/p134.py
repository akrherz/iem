"""This plot displays the period of consecutive days
    each year with the extreme criterion meet. In the case of a tie, the
    first period of the season is used for the analysis.  For a season to
    count within the analysis, it must have had at least 200 days with data.

    <p>The dew point option only works for ASOS networks and does a simple
    arthimetic mean of dew point temperatures.

<p>Note that the coldest and warmest feels like temperature values are
averages of the daily minimum or maximum values, not an average of an
average feels like temperature.  This is why we can't have nice things.</p>
"""
import datetime

import numpy as np
import pandas as pd
import matplotlib.colors as mpcolors
from matplotlib.colorbar import ColorbarBase
from matplotlib.ticker import MaxNLocator
from sqlalchemy import text
from pyiem.plot import get_cmap, figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound

PDICT = {
    "coldest_temp": "Coldest Average Temperature",
    "coldest_hitemp": "Coldest Average High Temperature",
    "coldest_lotemp": "Coldest Average Low Temperature",
    "coldest_lofeel": "Coldest Average Feels Like Temperature",
    "coldest_lodwpf": "Coldest Average Daily Low Dew Point Temperature",
    "warmest_temp": "Warmest Average Temperature",
    "warmest_hitemp": "Warmest Average High Temperature",
    "warmest_lotemp": "Warmest Average Low Temperature",
    "warmest_hifeel": "Warmest Average Daily High Feels Like Temperature",
    "warmest_hidwpf": "Warmest Average High Dew Point Temperature",
    "wettest": "Highest Precipitation",
}
# How to get plot variable from dataframe
XREF = {
    "coldest_temp": "avg_temp",
    "coldest_hitemp": "avg_hitemp",
    "coldest_lotemp": "avg_lotemp",
    "coldest_lofeel": "avg_lofeel",
    "coldest_lodwpf": "avg_lodwpf",
    "warmest_temp": "avg_temp",
    "warmest_hitemp": "avg_hitemp",
    "warmest_lotemp": "avg_lotemp",
    "warmest_hifeel": "avg_hifeel",
    "warmest_hidwpf": "avg_hidwpf",
    "wettest": "sum_precip",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"data": True, "cache": 86400, "description": __doc__}
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
    """Get the data"""
    days = ctx["days"]
    varname = ctx["var"]
    offset = 6 if varname.startswith("coldest") else 0
    station = ctx["station"]
    if ctx["network"].endswith("CLIMATE"):
        table = "alldata"
        dbname = "coop"
        highcol = "high"
        lowcol = "low"
        highdwpf = "null"
        lowdwpf = "null"
        highfeel = "null"
        lowfeel = "null"
        precipcol = "precip"
        stationcol = "station"
    else:
        station = ctx["_nt"].sts[station]["iemid"]
        dbname = "iem"
        highcol = "max_tmpf"
        lowcol = "min_tmpf"
        highdwpf = "max_dwpf"
        lowdwpf = "min_dwpf"
        highfeel = "max_feel"
        lowfeel = "min_feel"
        precipcol = "pday"
        table = "summary"
        stationcol = "iemid"
    with get_sqlalchemy_conn(dbname) as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH data as (
        SELECT day,
        extract(year from day + ':offset months'::interval) as season,
        avg(({highcol} + {lowcol})/2.)
            OVER (ORDER by day ASC ROWS :days preceding) as avg_temp,
        avg({highcol})
            OVER (ORDER by day ASC ROWS :days preceding) as avg_hitemp,
        avg({lowcol})
            OVER (ORDER by day ASC ROWS :days preceding) as avg_lotemp,
        avg({highfeel})
            OVER (ORDER by day ASC ROWS :days preceding) as avg_hifeel,
        avg({lowfeel})
            OVER (ORDER by day ASC ROWS :days preceding) as avg_lofeel,
        avg({highdwpf})
            OVER (ORDER by day ASC ROWS :days preceding) as avg_hidwpf,
        avg({lowdwpf})
            OVER (ORDER by day ASC ROWS :days preceding) as avg_lodwpf,
        sum({precipcol})
            OVER (ORDER by day ASC ROWS :days preceding) as sum_precip
        from {table} WHERE {stationcol} = :station and {highcol} is not null),
        agg1 as (
            SELECT season, day, avg_temp, avg_hitemp, avg_lotemp,
            sum_precip, avg_hidwpf, avg_lodwpf, avg_lofeel, avg_hifeel,
            row_number()
                OVER (PARTITION by season ORDER by avg_temp ASC nulls last,
                day ASC) as coldest_temp_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_hitemp ASC nulls last,
                day ASC) as coldest_hitemp_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_lotemp ASC nulls last,
                day ASC) as coldest_lotemp_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_lofeel ASC nulls last,
                day ASC) as coldest_lofeel_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_hidwpf DESC nulls last,
                day ASC) as warmest_hidwpf_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_temp DESC nulls last,
                day ASC) as warmest_temp_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_hitemp DESC nulls last,
                day ASC) as warmest_hitemp_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_hifeel DESC nulls last,
                day ASC) as warmest_hifeel_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_lotemp DESC nulls last,
                day ASC) as warmest_lotemp_rank,
            row_number()
                OVER (PARTITION by season ORDER by avg_lodwpf ASC nulls last,
                day ASC) as coldest_lodwpf_rank,
            row_number()
                OVER (PARTITION by season ORDER by sum_precip DESC nulls last,
                day ASC) as wettest_rank,
            count(*) OVER (PARTITION by season)
            from data)
        SELECT season, day,
        extract(doy from day - ':days days'::interval)::int as doy,
        avg_temp, avg_hitemp, avg_lotemp, avg_hidwpf, avg_lodwpf,
        avg_lofeel, avg_hifeel,
        sum_precip from agg1 where {varname}_rank = 1 and count > 200
        """
            ),
            conn,
            params={"days": days - 1, "offset": offset, "station": station},
            index_col="season",
        )
    if varname.startswith("coldest"):
        df.loc[df["doy"] < 183, "doy"] += 365.0
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    days = ctx["days"]
    varname = ctx["var"]
    df = get_data(ctx)
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    # Don't plot zeros for precip
    if varname == "wettest":
        df = df[df["sum_precip"] > 0]
    title = ctx["_sname"]
    subtitle = PDICT.get(varname)
    if days == 1:
        subtitle = subtitle.replace("Average ", "")
    subtitle = f"{days} Day Period with {subtitle}"
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.05, 0.3, 0.45, 0.54])
    lax = fig.add_axes([0.05, 0.1, 0.45, 0.2])
    cax = fig.add_axes([0.05, 0.875, 0.4, 0.02])
    cmap = get_cmap(ctx["cmap"])
    minval = df[XREF[varname]].min() - 1.0
    if varname == "wettest" and minval < 0:
        minval = 0
    maxval = df[XREF[varname]].max() + 1.0
    ramp = np.linspace(
        minval, maxval, min([int(maxval - minval), 10]), dtype="i"
    )
    norm = mpcolors.BoundaryNorm(ramp, cmap.N)
    ColorbarBase(cax, norm=norm, cmap=cmap, orientation="horizontal")
    units = "inch" if varname == "wettest" else r"$^\circ$F"
    fig.text(0.47, 0.88, units)
    bboxprops = dict(color="tan", alpha=0.5, boxstyle="round")
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
    lax.set_xlabel("Frequency of day within period")
    ax.set_ylim(df.index.values.min() - 3, df.index.values.max() + 3)

    ax.set_xlim(df["doy"].min() - 10, df["doy"].max() + 10)
    lax.set_xlim(df["doy"].min() - 10, df["doy"].max() + 10)
    ax.yaxis.set_major_locator(MaxNLocator(prune="lower"))

    # Plot per year
    series = df[XREF[varname]]
    ax = fig.add_axes([0.59, 0.5, 0.4, 0.4])
    ax.bar(df.index.values, series.values, color="blue", width=1)
    ax.set_ylim(bottom=series.min() - 5)
    ax.text(
        0.03,
        1.01,
        "Value by Year",
        transform=ax.transAxes,
        va="bottom",
        bbox=bboxprops,
    )
    ax.grid(True)

    # CDF
    ax = fig.add_axes([0.59, 0.1, 0.4, 0.3])
    X2 = np.sort(series.values)
    ptile = np.percentile(X2, [0, 5, 50, 95, 100])
    N = len(series.values)
    F2 = np.array(range(N)) / float(N) * 100.0
    ax.plot(X2, 100.0 - F2)
    ax.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    mysort = df.sort_values(by=XREF[varname], ascending=True)
    info = (
        f"Min: {series.min():.2f} {mysort.index[0]:.0f}\n"
        f"95th: {ptile[1]:.2f}\n"
        f"Mean: {series.mean():.2f}\n"
        f"STD: {series.std():.2f}\n"
        f"5th: {ptile[3]:.2f}\n"
        f"Max: {series.max():.2f} {mysort.index[-1]:.0f}"
    )
    ax.text(
        0.75,
        0.95,
        info,
        transform=ax.transAxes,
        va="top",
        bbox=dict(facecolor="white", edgecolor="k"),
    )
    ax.text(
        0.03,
        1.01,
        "Cumulative Distribution Function",
        transform=ax.transAxes,
        va="bottom",
        bbox=bboxprops,
    )
    ax.set_ylabel("Percentile")
    ax.grid(True)
    ax.set_xlabel(units)
    return fig, df


if __name__ == "__main__":
    plotter(dict(station="IA0112", var="wettest", network="IACLIMATE", days=3))
