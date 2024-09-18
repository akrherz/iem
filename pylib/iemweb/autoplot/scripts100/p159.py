"""
Based on available hourly observation reports
by METAR stations, this application presents the frequency of number
of hours for a given month or season at a given threshold.

<p>If you pick a custom day of the year period that crosses 1 January,
the year of the start date is used within the plot.</p>

<p>The hourly averages are based on years with sufficient data coverage (
&lt;20% missing). The blue bars indicate years with such amount of missing
data.</p>

<p>Please note that <strong>wind gusts</strong> were not recorded prior to
the early 1970s for most stations</p>
"""

from datetime import date, datetime

import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context
from sqlalchemy import text

from iemweb.autoplot.barchart import barchar_with_top10

MDICT = {
    "all": "No Month/Time Limit",
    "custom": "Custom/Pick Start + End Date",
    "ytd": f"Jan 1 through {date.today():%b %-d}",
    "jul1": "Jul 1 - Jun 30",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}

METRICS = {
    "tmpf": "Air Temp (F)",
    "dwpf": "Dew Point Temp (F)",
    "feel": "Feels Like Temp (F)",
    "mslp": "Mean Sea Level Pressure (mb)",
    "alti": "Pressure Altimeter (inHg)",
    "relh": "Relative Humidity (%)",
    "sped": "Wind Speed (mph)",
    "gust": "Wind Gust (mph)",
    "vsby": "Visibility (miles)",
}
UNITS = {
    "tmpf": "F",
    "dwpf": "F",
    "feel": "F",
    "relh": "%",
    "sped": "mph",
    "gust": "mph",
    "vsby": "miles",
    "mslp": "mb",
    "alti": "inHg",
}

DIRS = {"aoa": "At or Above", "below": "Below"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="dwpf",
            label="Which Variable",
            options=METRICS,
        ),
        dict(
            type="select",
            name="dir",
            default="aoa",
            label="Threshold Direction:",
            options=DIRS,
        ),
        dict(
            type="int",
            name="thres",
            default=65,
            label="Threshold (F, %, mph, inHg, mb):",
        ),
        dict(
            type="select",
            name="month",
            default="all",
            label="Date Limiter",
            options=MDICT,
        ),
        dict(
            type="sday",
            name="sdate",
            default="0101",
            label="Inclusive Start Day of Year (when Date Limiter is custom):",
        ),
        dict(
            type="sday",
            name="edate",
            default=f"{date.today():%m%d}",
            label="Inclusive End Day of Year (when Date Limiter is custom):",
        ),
        dict(
            type="year",
            min=1973,
            default=date.today().year,
            label="Year to Highlight",
            name="year",
        ),
        {
            "type": "year",
            "name": "syear",
            "default": 1920,
            "label": "Limit Data Analysis to inclusive start year:",
        },
    ]
    return desc


def set_df(ctx):
    """Set the dataframe"""
    offset = "ts"
    ctx["mlabel"] = (
        MDICT[ctx["month"]]
        if ctx["month"] != "jul1"
        else "Jul-Jun [year of Jul shown]"
    )
    ctx["totaldays"] = 0
    months = list(range(1, 13))
    doylimit = ""
    if ctx["month"] in ["all", "jul1", "ytd"]:
        if ctx["month"] == "jul1":
            offset = "ts - '6 months'::interval"
    elif ctx["month"] == "custom":
        doylimit = (
            " and to_char(ts, 'mmdd') >= :sdate and "
            "to_char(ts, 'mmdd') <= :edate "
        )
        ctx["totaldays"] = (ctx["edate"] - ctx["sdate"]).days + 1
        ctx["mlabel"] = f" {ctx['sdate']:%b %-d} thru {ctx['edate']:%b %-d}"
        if ctx["sdate"] > ctx["edate"]:
            ctx["totaldays"] = (
                ctx["edate"].replace(year=2001) - ctx["sdate"]
            ).days + 1
            days = (ctx["edate"] - date(2000, 1, 1)).days + 1
            offset = f"ts - '{days} days'::interval"
            doylimit = (
                " and (to_char(ts, 'mmdd') >= :sdate or "
                "to_char(ts, 'mmdd') <= :edate) "
            )
    elif ctx["month"] == "fall":
        months = [9, 10, 11]
    elif ctx["month"] == "winter":
        months = [12, 1, 2]
        offset = "ts + '1 month'::interval"
    elif ctx["month"] == "spring":
        months = [3, 4, 5]
    elif ctx["month"] == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.strptime(f"2000-{ctx['month']}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]
    ctx["months"] = months
    opp = ">=" if ctx["dir"] == "aoa" else "<"

    dbvarname = ctx["var"]
    if ctx["var"] == "sped":
        dbvarname = "(sknt * 1.15)"
    elif ctx["var"] == "gust":
        dbvarname = "(gust * 1.15)"
    if ctx["month"] == "ytd":
        doylimit = " and to_char(ts, 'mmdd') <= :sday "
    with get_sqlalchemy_conn("asos") as conn:
        ctx["df"] = pd.read_sql(
            text(
                f"""WITH hourly as (
            SELECT date_trunc('hour', valid + '10 minutes'::interval)
            at time zone :tzname as ts,
            case when {dbvarname}::int {opp} :t then 1 else 0 end as hit
            from alldata where station = :station and report_type = 3 and
            valid > :start)

            SELECT extract(year from {offset})::int as year,
            extract(hour from ts)::int as hour,
            sum(hit) as hits, count(*) as obs from hourly
            WHERE extract(month from ts) = ANY(:months) {doylimit}
            GROUP by year, hour
            """
            ),
            conn,
            params={
                "tzname": ctx["_nt"].sts[ctx["zstation"]]["tzname"],
                "t": ctx["thres"],
                "station": ctx["zstation"],
                "months": months,
                "sday": date.today().strftime("%m%d"),
                "sdate": ctx["sdate"].strftime("%m%d"),
                "edate": ctx["edate"].strftime("%m%d"),
                "start": f"{ctx['syear']}-01-01",
            },
            index_col=None,
        )
    if ctx["df"].empty:
        raise NoDataFound("Error, no results returned!")


def set_fig(ctx):
    """Set the plot"""
    ydf = ctx["df"].groupby("year").sum()
    title = (
        f"({ctx['mlabel']}) {METRICS[ctx['var']]} Hours {DIRS[ctx['dir']]} "
        f"{ctx['thres']}{UNITS[ctx['var']]}\n"
        f"{ctx['_sname']}:: ({ydf.index.min():.0f}-{ydf.index.max():.0f})"
    )
    # Loop over plot years and background highlight any years with less than
    # 80% data coverage
    obscount = len(ctx["months"]) * 30 * 24 * 0.8
    if ctx["month"] == "ytd":
        obscount = int(f"{date.today():%j}") * 24 * 0.8
    elif ctx["month"] == "custom":
        obscount = ctx["totaldays"] * 24 * 0.8
    ctx["fig"] = figure(apctx=ctx, title=title)
    quorum = ydf[ydf["obs"] > obscount]
    ax = barchar_with_top10(
        ctx["fig"],
        quorum,
        "hits",
        color="green",
        table_col_title="Hours",
    )
    antiquorum = ydf[ydf["obs"] < obscount]
    ax.bar(
        antiquorum.index.values,
        antiquorum["hits"],
        width=1,
        align="center",
        color="green",
    )
    ax.set_position((0.07, 0.6, 0.68, 0.3))
    for _year in range(ydf.index.values[0], ydf.index.values[-1] + 1):
        if _year not in ydf.index or ydf.at[_year, "obs"] < obscount:
            ax.axvspan(_year - 0.5, _year + 0.5, color="#cfebfd", zorder=-3)
    if ctx["year"] in ydf.index.values:
        val = ydf.loc[ctx["year"]]
        ax.bar(
            ctx["year"],
            val["hits"],
            align="center",
            fc="orange",
            ec="orange",
            zorder=5,
        )
    ax.grid(True)
    ax.set_ylabel("Hours")
    ax.set_xlim(ydf.index.min() - 0.5, ydf.index.max() + 0.5)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Years with blue shading have more than 20% missing data")
    avgv = ydf["hits"].mean()
    ax.axhline(avgv, color="k", zorder=10)
    ax.text(ydf.index.max() + 0.7, avgv, f"Avg\n{avgv:.1f}", va="center")

    df2 = ydf[ydf["obs"] > obscount]
    years = len(df2.index)
    df2 = ctx["df"][ctx["df"]["year"].isin(df2.index.values)]
    hdf = df2.groupby("hour").sum() / years
    ax1 = ctx["fig"].add_axes([0.07, 0.1, 0.68, 0.4])
    ax1.bar(
        hdf.index.values,
        hdf["hits"],
        align="center",
        fc="b",
        ec="b",
        label="Avg",
    )
    thisyear = ctx["df"][ctx["df"]["year"] == ctx["year"]]
    if not thisyear.empty:
        ax1.bar(
            thisyear["hour"].values,
            thisyear["hits"],
            align="center",
            width=0.25,
            zorder=5,
            fc="orange",
            ec="orange",
            label=f"{ctx['year']}",
        )
    ax1.set_xlim(-0.5, 23.5)
    ax1.grid(True)
    ax1.legend(loc=(0.7, -0.22), ncol=2, fontsize=10)
    ax1.set_ylabel("Days Per Period")
    ax1.set_xticks(range(0, 24, 4))
    ax1.set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax1.set_xlabel(
        f"Hour of Day ({ctx['_nt'].sts[ctx['zstation']]['tzname']})",
        ha="right",
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    set_df(ctx)
    set_fig(ctx)

    return ctx["fig"], ctx["df"]
