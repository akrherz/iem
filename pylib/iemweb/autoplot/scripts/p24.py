"""
The map presents IEM computed climate district or statewide
values for a metric of your choice.  This map can be generated for a given
month and year or period of dates.  If the period of days includes leap
day, this day is included and unweighted against years without it.  If the
period spans two years, the presented year on the map represents the
second year in the selection.  For plotting period Option 2, the time
period is limited to 1 year or less.

<p>The data uses the current NWS COOP nomenclature of
reporting each day at approximately 7 AM.  So for example, a plot of June
precipitation would stricly include the period of 7 AM 31 May
to 7 AM 30 June. Data for the current date is available at approximately
noon central time each day.</p>

<p><strong>Aridity Note</strong>: Presently, this autoplot can only plot the
value and not departures nor ranks.  Hopefully, this can be implemented in
the near future.</p>
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot, centered_bins, get_cmap, pretty_bins
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "aridity": "Aridity Index",
    "avgt": "Average Temperature",
    "high": "Average High Temperature",
    "low": "Average Low Temperature",
    "sdd86": "Stress Degree Days (Base 86)",
    "precip": "Total Precipitation",
}

PDICT2 = {
    "month": "Plot by Month(s) [Option 1]",
    "day": "Plot by Inclusive Date Period [Option 2]",
}
PDICT3 = {
    "cd": "Climate District",
    "st": "State",
}
PDICT4 = {
    "rank": "Ranks",
    "val": "Values",
    "dep": "Departures",
}

MDICT = {
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
    desc = {"description": __doc__, "data": True, "cache": 86400}
    today = date.today()
    lmonth = today - timedelta(days=28)
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT3,
            default="cd",
            name="which",
            label="Plot Climate Districts or States:",
        ),
        dict(
            type="csector",
            name="csector",
            default="midwest",
            label="Area to Plot:",
        ),
        dict(
            type="select",
            name="var",
            default="precip",
            label="Select Variable",
            options=PDICT,
        ),
        {
            "type": "select",
            "options": PDICT4,
            "default": "rank",
            "name": "w",
            "label": "Select aggregate to plot",
        },
        dict(
            type="select",
            name="p",
            default="month",
            label="Plotting Period",
            options=PDICT2,
        ),
        dict(
            type="year",
            name="year",
            default=lmonth.year,
            label="[Option 1] Select Year:",
            min=1893,
        ),
        dict(
            type="select",
            name="month",
            default=lmonth.month,
            label="[Option 1] Month Limiter",
            options=MDICT,
        ),
        dict(
            type="date",
            name="sdate",
            default=lmonth.strftime("%Y/%m/%d"),
            label="[Option 2] Start Date",
            min="1893/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="[Option 2] End Date (inclusive)",
            min="1893/01/01",
        ),
        dict(type="cmap", name="cmap", default="BrBG_r", label="Color Ramp:"),
    ]
    return desc


def get_daily_data(ctx, sdate, edate):
    """Do the data work"""
    edate = min([edate, date.today()])
    if edate <= sdate:
        raise NoDataFound("start date after end date, please correct")
    if (edate - sdate).days > 366:
        raise NoDataFound(
            "Sorry, too long of period selected. < 1 year please"
        )
    params = {
        "year": edate.year,
        "sdate": sdate.strftime("%m%d"),
        "edate": edate.strftime("%m%d"),
        "csector": ctx["csector"],
    }
    yearcond = "false"
    if edate.year != sdate.year:
        yearcond = "sday >= :sdate"
        sday = " ( sday >= :sdate or sday <= :edate ) "
    else:
        sday = " sday >= :sdate and sday <= :edate "

    table = "alldata"
    if len(ctx["csector"]) == 2 and ctx["which"] != "st":
        table = f"alldata_{ctx['csector']}"
    if ctx["which"] == "st":
        params["stations"] = [f"{st}0000" for st in state_names]
    else:
        params["stations"] = [
            f"{st}C{x:03.0f}" for st in state_names for x in range(1, 11)
        ]

    with get_sqlalchemy_conn("coop") as conn:
        ctx["df"] = pd.read_sql(
            text(f"""
        with monthly as (
            SELECT
            case when {yearcond} then year + 1 else year end as myyear,
            station,
            sum(sdd86(high, low)) as sdd86,
            sum(precip) as p,
            avg((high+low)/2.) as avgt,
            avg(low) as avglo,
            avg(high) as avghi,
            max(day) as max_date
            from {table}
            WHERE station = ANY(:stations) and {sday}
            GROUP by myyear, station),
        ranks as (
            SELECT station, myyear as year,
            max(max_date) OVER (PARTITION by station, myyear) as max_date,
            avg(sdd86) OVER (PARTITION by station) as avg_sdd86,
            sdd86 as sdd86,
            avg(p) OVER (PARTITION by station) as avg_precip,
            stddev(p) OVER (PARTITION by station) as std_precip,
            p as precip,
            avg(avghi) OVER (PARTITION by station) as avg_high,
            stddev(avghi) OVER (PARTITION by station) as std_high,
            avghi as high,
            avg(avgt) OVER (PARTITION by station) as avg_avgt,
            avgt,
            avg(avglo) OVER (PARTITION by station) as avg_low,
            avglo as low,
            rank() OVER (PARTITION by station ORDER by p DESC) as precip_rank,
            rank() OVER (PARTITION by station ORDER by avghi DESC)
                as high_rank,
            rank() OVER (PARTITION by station ORDER by avglo DESC) as low_rank,
            rank() OVER (PARTITION by station ORDER by avgt DESC) as avgt_rank,
            rank() OVER (PARTITION by station ORDER by sdd86 DESC)
                as sdd86_rank
            from monthly)

        SELECT station,
        high as high_val, low as low_val, precip as precip_val,
        avgt as avgt_val, sdd86 as sdd86_val,
        high - avg_high as high_dep, low - avg_low as low_dep,
        precip - avg_precip as precip_dep, avgt - avg_avgt as avgt_dep,
        sdd86 - avg_sdd86 as sdd86_dep,
        precip_rank, avgt_rank, high_rank, low_rank, sdd86_rank,
        ((high - avg_high) / std_high) - ((precip - avg_precip) / std_precip)
        as aridity, max_date from ranks where year = :year
        """),
            conn,
            params=params,
            index_col="station",
        )
    if ctx["df"].empty:
        raise NoDataFound("No data found")
    edate = ctx["df"]["max_date"].max()
    dl = (sdate - timedelta(days=1)).strftime("%-d %b %Y")
    ctx["label"] = f"{dl} ~7 AM till {edate:%-d %b %Y} ~7 AM"


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    if ctx["p"] == "day":
        get_daily_data(ctx, ctx["sdate"], ctx["edate"])
    else:
        oneday = timedelta(days=1)
        year = ctx["year"]
        month = ctx["month"]
        if month == "fall":
            sts = date(year, 9, 1)
            ets = date(year, 11, 30)
        elif month == "winter":
            sts = date(year, 12, 1)
            ets = date(year + 1, 3, 1) - oneday
        elif month == "spring":
            sts = date(year, 3, 1)
            ets = date(year, 5, 31)
        elif month == "summer":
            sts = date(year, 6, 1)
            ets = date(year, 8, 31)
        else:
            sts = date(year, int(month), 1)
            ets = (sts + timedelta(days=34)).replace(day=1) - oneday

        get_daily_data(ctx, sts, ets)
    ctx["lastyear"] = date.today().year
    ctx["years"] = ctx["lastyear"] - 1893 + 1

    subtitle = "Based on IEM Estimates"
    title = "Ranks "
    units = ""
    if ctx["var"] == "aridity":
        subtitle = "Std Average High Temp Departure minus Std Precip Departure"
        title = ""
        if ctx["w"] == "dep":
            raise NoDataFound("Aridity does not have departures")
    elif ctx["w"] == "dep":
        title = "Departure "
        if ctx["var"] in ["high", "low", "avgt", "sdd86"]:
            units = "degrees F"
        elif ctx["var"] == "precip":
            units = "inch"
    elif ctx["w"] == "val":
        title = ""
        if ctx["var"] in ["high", "low", "avgt", "sdd86"]:
            units = "degrees F"
        elif ctx["var"] == "precip":
            units = "inch"
    elif ctx["w"] == "rank":
        subtitle += (
            ", 1 is "
            f"{'wettest' if ctx['var'] == 'precip' else 'hottest'} out of "
            f"{ctx['years']} total years (1893-{ctx['lastyear']})"
        )
    if ctx["w"] == "rank":
        units = ""
    mp = MapPlot(
        apctx=ctx,
        continentalcolor="white",
        title=(
            f"{ctx['label']} {PDICT[ctx['var']]} {title}"
            f"by {PDICT3[ctx['which']]}"
        ),
        subtitle=subtitle,
        titlefontsize=14,
        nocaption=True,
    )
    cmap = get_cmap(ctx["cmap"])
    pvar = f"{ctx['var']}_{ctx['w']}"
    fmt = "%.2f"
    if ctx["var"] == "sdd86":
        fmt = "%.1f"
    if ctx["var"] == "aridity":
        bins = np.arange(-4, 4.1, 1)
        pvar = ctx["var"]
        fmt = "%.1f"
    elif ctx["w"] == "rank":
        bins = [
            1,
            5,
            10,
            25,
            50,
            75,
            100,
            ctx["years"] - 10,
            ctx["years"] - 5,
            ctx["years"],
        ]
        fmt = "%.0f"
    elif ctx["w"] == "val":
        bins = pretty_bins(ctx["df"][pvar].min(), ctx["df"][pvar].max())
    else:  # dep
        bins = centered_bins(ctx["df"][pvar].abs().max())
    if ctx["which"] == "st":
        ctx["df"].index = ctx["df"].index.str.slice(0, 2)
        mp.fill_states(
            ctx["df"][pvar],
            ilabel=True,
            plotmissing=False,
            lblformat=fmt,
            bins=bins,
            cmap=cmap,
            units=units,
        )
    else:
        mp.fill_climdiv(
            ctx["df"][pvar],
            ilabel=True,
            plotmissing=False,
            lblformat=fmt,
            bins=bins,
            cmap=cmap,
            units=units,
        )

    return mp.fig, ctx["df"]
