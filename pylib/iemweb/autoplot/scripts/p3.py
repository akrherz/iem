"""
This plot displays a single month's worth of data
over all of the years in the period of record.  In most cases, you can
access the raw data for these plots
<a href="/climodat/" class="link link-info">here.</a>  For the variables
comparing the daily temperatures against average, the average is taken
from the NCEI current 1981-2010 climatology.

<p>This page presents a number of statistical measures.  In general, these
can be summarized as:
<ul>
    <li><strong>Average:</strong> simple arithmetic mean</li>
    <li><strong>Maximum:</strong> the largest single day value</li>
    <li><strong>Standard Deviation:</strong> measure indicating the spread
    within the population of daily values for each grouped period.  Lower
    values indicate less variability within the month or period.</li>
    <li><strong>Average Day to Day:</strong> this is computed by sequentially
    ordering the daily observations with time, computing the absolute value
    between the current day and previous day and then averaging those values.
    This is another measure of variability during the month.</li>
    </ul></p>

<p>You can optionally summarize by decades.  For this plot and for example,
the decade of the 90s represents the inclusive years 1990 thru 1999.
Please use care to specify start and end years that make sense for this
presentation.  For example, if the year is only 2020, the 2020 decade
values would only have one year included!</p>
"""

import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {
    "max-high": "Maximum High",
    "avg-high": "Average High",
    "std-high": "Standard Deviation High",
    "delta-high": "Average Day to Day High Change",
    "min-high": "Minimum High",
    "max-low": "Maximum Low",
    "avg-low": "Average Low",
    "std-low": "Standard Deviation Low",
    "delta-low": "Average Day to Day Low Change",
    "min-low": "Minimum Low",
    "avg-temp": "Average Temp",
    "std-temp": "Standard Deviation of Average Temp",
    "delta-temp": "Average Day to Day Avg Temp Change",
    "range-avghi-avglo": "Range between Average High + Average Low",
    "max-precip": "Maximum Daily Precip",
    "sum-precip": "Total Precipitation",
    "days-high-above": (
        "Days with High Temp Greater Than or Equal To (threshold)"
    ),
    "days-high-below": "Days with High Temp Below (threshold)",
    "days-high-above-avg": (
        "Days with High Temp Greater Than or Equal To Average"
    ),
    "days-lows-above": (
        "Days with Low Temp Greater Than or Equal To (threshold)"
    ),
    "days-lows-below": "Days with Low Temp Below (threshold)",
    "days-lows-below-avg": "Days with Low Temp Below Average",
    "days-precip-above": "Days with Precipitation Above (threshold)",
}
PDICT2 = {"no": "Plot Yearly Values", "yes": "Plot Decadal Values"}
MDICT = {
    "year": "Calendar Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="month",
            default=today.month,
            label="Month/Season",
            options=MDICT,
        ),
        dict(
            type="select",
            name="type",
            default="max-high",
            label="Which metric to plot?",
            options=PDICT,
        ),
        dict(
            type="float",
            name="threshold",
            default="-99",
            label="Threshold (optional, specify when appropriate):",
        ),
        dict(
            type="year",
            default=1850,
            label="Potential Minimum Year (inclusive) to use in plot:",
            name="syear",
            min=1850,
        ),
        dict(
            type="year",
            default=today.year,
            label="Potential Maximum Year (inclusive) to use in plot:",
            name="eyear",
            min=1850,
        ),
        dict(
            type="select",
            options=PDICT2,
            name="decadal",
            default="no",
            label="Aggregate plot by decades:",
        ),
    ]
    return desc


def get_highcharts(ctx: dict) -> str:
    """Go high charts"""
    add_ctx(ctx)
    ptinterval = "10" if ctx["decadal"] else "1"
    containername = ctx["_e"]
    ylabel = ctx["ylabel"].replace(r"$^\circ$", "")
    return f"""
Highcharts.chart('{containername}', {{
    title: {{text: '{ctx["title"]}'}},
    subtitle: {{text: '{ctx["subtitle"]}'}},
    chart: {{zoomType: 'x'}},
    tooltip: {{shared: true}},
    xAxis: {{title: {{text: '{ctx["xlabel"]}'}}}},
    yAxis: {{title: {{text: '{ylabel}'}}}},
    series: [{{
        name: '{ctx["ptype"]}',
        type: 'column',
        width: 0.8,
        pointStart: {ctx["df"].index.min()},
        pointInterval: {ptinterval},
        tooltip: {{
            valueDecimals: 2
        }},
        data: {str(ctx["data"].tolist())},
        threshold: null
        }}, {{
        tooltip: {{valueDecimals: 2}},
        name: '30 Year Trailing Avg',
    pointStart: {str(ctx["df"].index.min() + (3 if ctx["decadal"] else 30))},
        pointInterval: {ptinterval},
            width: 2,
        data: {str(ctx["tavg"][(3 if ctx["decadal"] else 30) :])}
        }},{{
            tooltip: {{
                valueDecimals: 2
            }},
            name: 'Average',
            width: 2,
            pointPadding: 0.1,
            pointStart: {str(ctx["df"].index.min())},
            pointInterval: {ptinterval},
            data: {str([ctx["avgv"]] * len(ctx["df"].index))}
        }}]
}});
    """


def add_ctx(ctx):
    """Get the context"""
    ctx["decadal"] = ctx.get("decadal") == "yes"
    # Lower the start year if decadal
    if ctx["decadal"]:
        ctx["syear"] -= ctx["syear"] % 10
    station = ctx["station"]
    month = ctx["month"]
    ptype = ctx["type"]
    threshold = ctx["threshold"]

    lag = "0 days"
    if month == "fall":
        months = [9, 10, 11]
        label = "Fall (SON)"
    elif month == "winter":
        months = [12, 1, 2]
        lag = "31 days"
        label = "Winter (DJF)"
    elif month == "spring":
        months = [3, 4, 5]
        label = "Spring (MAM)"
    elif month == "summer":
        months = [6, 7, 8]
        label = "Summer (JJA)"
    elif month == "year":
        months = list(range(1, 13))
        label = "Calendar Year"
    else:
        months = [int(month)]
        label = calendar.month_name[int(month)]

    decagg = 10 if ctx["decadal"] else 1
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                f"""
        WITH climo as (
            SELECT to_char(valid, 'mmdd') as sday,
            high, low from ncei_climate91 WHERE station = :ncei),
        day2day as (
            SELECT
            extract(year from day + '{lag}'::interval)::int / {decagg}
                as myyear,
            month,
            abs(high - lag(high) OVER (ORDER by day ASC)) as dhigh,
            abs(low - lag(low) OVER (ORDER by day ASC)) as dlow,
            abs((high+low)/2. - lag((high+low)/2.)
                OVER (ORDER by day ASC)) as dtemp
            from alldata WHERE station = :station),
        agg as (
            SELECT myyear, avg(dhigh) as dhigh, avg(dlow) as dlow,
            avg(dtemp) as dtemp from day2day
            WHERE month = ANY(:months) GROUP by myyear),
        agg2 as (
            SELECT
            extract(year from day + '{lag}'::interval)::int / {decagg}
                as myyear,
            max(o.year) - min(o.year) + 1 as years,
            max(o.high) as "max-high",
            min(o.high) as "min-high",
            avg(o.high) as "avg-high",
            stddev(o.high) as "std-high",
            max(o.low) as "max-low",
            min(o.low) as "min-low",
            avg(o.low) as "avg-low",
            stddev(o.low) as "std-low",
            avg((o.high + o.low)/2.) as "avg-temp",
            stddev((o.high + o.low)/2.) as "std-temp",
            max(o.precip) as "max-precip",
            sum(o.precip) as "sum-precip",
            avg(o.high) - avg(o.low) as "range-avghi-avglo",
            sum(case when o.high::numeric >= :t then 1 else 0 end)
                as "days-high-above",
            sum(case when o.high::numeric < :t then 1 else 0 end)
                as "days-high-below",
            sum(case when o.high::numeric >= c.high then 1 else 0 end)
                as "days-high-above-avg",
            sum(case when o.low::numeric >= :t then 1 else 0 end)
                as "days-lows-above",
            sum(case when o.low::numeric < c.low then 1 else 0 end)
                as "days-lows-below-avg",
            sum(case when o.low::numeric < :t then 1 else 0 end)
                as "days-lows-below",
            sum(case when o.precip::numeric >= :t then 1 else 0 end)
                as "days-precip-above"
            from alldata o JOIN climo c on (o.sday = c.sday)
        where station = :station and month = ANY(:months) GROUP by myyear)

        SELECT b.*, a.dhigh as "delta-high", a.dlow as "delta-low",
        a.dtemp as "delta-temp" from agg a JOIN agg2 b
        on (a.myyear = b.myyear) WHERE b.myyear * {decagg} >= :syear
        and b.myyear * {decagg} <= :eyear
        ORDER by b.myyear ASC
        """
            ),
            conn,
            params={
                "ncei": ctx["_nt"].sts[station]["ncei91"],
                "station": station,
                "months": months,
                "t": threshold,
                "syear": ctx["syear"],
                "eyear": ctx["eyear"],
            },
            index_col="myyear",
        )
    if df.empty:
        raise NoDataFound("No data was found for query")
    if ctx["decadal"]:
        df.index = df.index * 10
        # Need to fix the sum() operations above
        for colname in [
            "sum-precip",
            "days-high-above",
            "days-high-below",
            "days-high-above-avg",
            "days-lows-above",
            "days-lows-below-avg",
            "days-lows-below",
            "days-precip-above",
        ]:
            df[colname] = df[colname] / df["years"]

    # Figure out the max min values to add to the row
    df2 = df[df[ptype] == df[ptype].max()]
    if df2.empty:
        raise NoDataFound("No data was found for query")
    df = df.dropna()
    xx = "+" if len(df2.index) > 1 else ""
    xlabel = f"Year, Max: {df[ptype].max():.2f} {df2.index.values[0]}{xx}"
    df2 = df[df[ptype] == df[ptype].min()]
    xx = "+" if len(df2.index) > 1 else ""
    xlabel += f", Min: {df[ptype].min():.2f} {df2.index.values[0]}{xx}"
    ctx["xlabel"] = xlabel
    data = df[ptype].values
    ctx["data"] = data
    ctx["avgv"] = df[ptype].mean()
    ctx["df"] = df
    # Compute 30 year trailing average
    tavg = [None] * 30
    for i in range(30, len(data)):
        tavg.append(np.average(data[i - 30 : i]))
    if ctx["decadal"]:
        tavg = [None] * 3
        for i in range(3, len(data)):
            tavg.append(np.average(data[i - 3 : i]))

    ctx["tavg"] = tavg
    # End interval is inclusive
    ctx["a1981_2010"] = df.loc[1981:2010, ptype].mean()
    ctx["ptype"] = ptype
    ctx["station"] = station
    ctx["threshold"] = threshold
    ctx["month"] = month
    ctx["title"] = f"{ctx['_sname']} {df.index.min()}-{df.index.max()}"
    ctx["subtitle"] = f"{label} {PDICT[ptype]}"
    if ptype.find("days") == 0 and ptype.find("avg") == -1:
        ctx["subtitle"] += f" ({threshold})"

    units = r"$^\circ$F"
    if ctx["ptype"].find("precip") > 0:
        units = "inches"
    elif ctx["ptype"].find("days") > 0:
        units = "days"
    ctx["ylabel"] = f"{PDICT[ctx['ptype']]} [{units}]"
    return ctx


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    add_ctx(ctx)

    (fig, ax) = figure_axes(
        title=ctx["title"],
        subtitle=ctx["subtitle"],
        apctx=ctx,
    )
    ax.set_position([0.1, 0.1, 0.7, 0.8])

    colorabove = "tomato"
    colorbelow = "dodgerblue"
    precision = "%.1f"
    if ctx["ptype"] in ["max-precip", "sum-precip", "days-precip-above"]:
        colorabove = "dodgerblue"
        colorbelow = "tomato"
        precision = "%.2f"
    bars = ax.bar(
        ctx["df"].index.values,
        ctx["data"],
        color=colorabove,
        align="edge",
        width=9 if ctx["decadal"] else 1,
    )
    for i, mybar in enumerate(bars):
        if ctx["data"][i] < ctx["avgv"]:
            mybar.set_color(colorbelow)
    lbl = "Avg: " + precision % (ctx["avgv"],)
    ax.axhline(ctx["avgv"], lw=2, color="k", zorder=2, label=lbl)
    lbl = "1981-2010: " + precision % (ctx["a1981_2010"],)
    ax.axhline(ctx["a1981_2010"], lw=2, color="brown", zorder=2, label=lbl)
    if len(ctx["tavg"]) > 30:
        ax.plot(
            ctx["df"].index.values,
            ctx["tavg"],
            lw=1.5,
            color="g",
            zorder=4,
            label="Trailing 30yr",
        )
        ax.plot(
            ctx["df"].index.values, ctx["tavg"], lw=3, color="yellow", zorder=3
        )
    ax.set_xlim(
        ctx["df"].index.min() - 1,
        ctx["df"].index.max() + (11 if ctx["decadal"] else 1),
    )
    if ctx["ptype"].find("precip") == -1 and ctx["ptype"].find("days") == -1:
        ax.set_ylim(min(ctx["data"]) - 5, max(ctx["data"]) + 5)

    ax.set_xlabel(ctx["xlabel"])
    ax.set_ylabel(ctx["ylabel"])
    ax.grid(True)
    ax.legend(ncol=3, loc="best", fontsize=10)

    # Print out the top 10 years and bottom 10 years
    if not ctx["decadal"]:
        label = "Top 10 Years"
        for idx, row in (
            ctx["df"]
            .sort_values(ctx["ptype"], ascending=False)
            .head(10)
            .iterrows()
        ):
            yr = f"{idx - 1}-{idx}" if ctx["month"] == "winter" else f"{idx}"
            label += f"\n{yr}: {precision % row[ctx['ptype']]}"
        fig.text(
            0.81,
            0.89,
            label,
            ha="left",
            va="top",
        )
        label = "Bottom 10 Years"
        for idx, row in (
            ctx["df"]
            .sort_values(ctx["ptype"], ascending=True)
            .head(10)
            .iterrows()
        ):
            yr = f"{idx - 1}-{idx}" if ctx["month"] == "winter" else f"{idx}"
            label += f"\n{yr}: {precision % row[ctx['ptype']]}"
        fig.text(
            0.81,
            0.49,
            label,
            ha="left",
            va="top",
        )

    return fig, ctx["df"]
