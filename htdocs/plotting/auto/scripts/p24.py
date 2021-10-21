"""Climate District ranks"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "aridity": "Aridity Index",
    "avgt": "Average Temperature",
    "high": "Average High Temperature",
    "low": "Average Low Temperature",
    "precip": "Total Precipitation",
}

PDICT2 = {
    "month": "Plot by Month(s) [Option 1]",
    "day": "Plot by Inclusive Date Period [Option 2]",
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
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """The map presents IEM computed climate district
    ranks for a metric of your choice.  This map can be generated for a given
    month and year or period of dates.  If the period of days includes leap
    day, this day is included and unweighted against years without it.  If the
    period spans two years, the presented year on the map represents the
    second year in the selection.  For plotting period Option 2, the time
    period is limited to 1 year or less.

    <p>The climate district data uses the current NWS COOP nomenclature of
    reporting each day at approximately 7 AM.  So for example, a plot of June
    precipitation would stricly include the period of 7 AM 31 May
    to 7 AM 30 June. Data for the current date is available at approximately
    noon each day.
    """
    today = datetime.date.today()
    lmonth = today - datetime.timedelta(days=28)
    desc["arguments"] = [
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
    edate = min([edate, datetime.date.today()])
    if edate <= sdate:
        raise NoDataFound("start date after end date, please correct")
    if (edate - sdate).days > 366:
        raise NoDataFound(
            "Sorry, too long of period selected. < 1 year please"
        )
    pgconn = get_dbconn("coop")
    yearcond = "false"
    if edate.year != sdate.year:
        yearcond = f"sday >= '{sdate.strftime('%m%d')}'"
        sday = " sday >= '%s' or sday <= '%s' " % (
            sdate.strftime("%m%d"),
            edate.strftime("%m%d"),
        )
    else:
        sday = " sday >= '%s' and sday <= '%s' " % (
            sdate.strftime("%m%d"),
            edate.strftime("%m%d"),
        )

    statelimiter = ""
    table = "alldata"
    if len(ctx["csector"]) == 2:
        statelimiter = (" and substr(station, 1, 2) = '%s' ") % (
            ctx["csector"],
        )
        table = "alldata_%s" % (ctx["csector"],)

    ctx["df"] = read_sql(
        f"""
    with monthly as (
        SELECT
        case when {yearcond} then year + 1 else year end as myyear,
        station,
        sum(precip) as p,
        avg((high+low)/2.) as avgt,
        avg(low) as avglo,
        avg(high) as avghi,
        max(day) as max_date
        from {table}
        WHERE substr(station, 3, 1) = 'C' and ( {sday} ) {statelimiter}
        GROUP by myyear, station),
    ranks as (
        SELECT station, myyear as year,
        max(max_date) OVER (PARTITION by station, myyear) as max_date,
        avg(p) OVER (PARTITION by station) as avg_precip,
        stddev(p) OVER (PARTITION by station) as std_precip,
        p as precip,
        avg(avghi) OVER (PARTITION by station) as avg_high,
        stddev(avghi) OVER (PARTITION by station) as std_high,
        avghi as high,
        avg(avglo) OVER (PARTITION by station) as avg_low,
        stddev(avglo) OVER (PARTITION by station) as std_low,
        avglo as low,
        rank() OVER (PARTITION by station ORDER by p DESC) as precip_rank,
        rank() OVER (PARTITION by station ORDER by avghi DESC) as high_rank,
        rank() OVER (PARTITION by station ORDER by avglo DESC) as low_rank,
        rank() OVER (PARTITION by station ORDER by avgt DESC) as avgt_rank
        from monthly)

    SELECT station, precip_rank, avgt_rank, high_rank, low_rank,
    ((high - avg_high) / std_high) - ((precip - avg_precip) / std_precip)
    as aridity, max_date from ranks where year = %s
    """,
        pgconn,
        params=(edate.year,),
        index_col="station",
    )
    if ctx["df"].empty:
        raise NoDataFound("No data found")
    edate = ctx["df"]["max_date"].max()
    ctx["label"] = "%s ~7 AM till %s ~7 AM" % (
        (sdate - datetime.timedelta(days=1)).strftime("%-d %b %Y"),
        edate.strftime("%-d %b %Y"),
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    if ctx["p"] == "day":
        get_daily_data(ctx, ctx["sdate"], ctx["edate"])
    else:
        oneday = datetime.timedelta(days=1)
        year = ctx["year"]
        month = ctx["month"]
        if month == "fall":
            sts = datetime.date(year, 9, 1)
            ets = datetime.date(year, 11, 30)
        elif month == "winter":
            sts = datetime.date(year, 12, 1)
            ets = datetime.date(year, 3, 1) - oneday
        elif month == "spring":
            sts = datetime.date(year, 3, 1)
            ets = datetime.date(year, 5, 31)
        elif month == "summer":
            sts = datetime.date(year, 6, 1)
            ets = datetime.date(year, 8, 31)
        else:
            sts = datetime.date(year, int(month), 1)
            ets = (sts + datetime.timedelta(days=34)).replace(day=1) - oneday

        get_daily_data(ctx, sts, ets)
    ctx["lastyear"] = datetime.date.today().year
    ctx["years"] = ctx["lastyear"] - 1893 + 1
    csector = ctx["csector"]

    subtitle = (
        "Based on IEM Estimates, " "1 is %s out of %s total years (1893-%s)"
    ) % (
        "wettest" if ctx["var"] == "precip" else "hottest",
        ctx["years"],
        ctx["lastyear"],
    )
    if ctx["var"] == "aridity":
        subtitle = "Std Average High Temp Departure minus Std Precip Departure"
    mp = MapPlot(
        sector=("state" if len(csector) == 2 else csector),
        state=ctx["csector"],
        continentalcolor="white",
        title="%s %s %sby Climate District"
        % (
            ctx["label"],
            PDICT[ctx["var"]],
            "Ranks " if ctx["var"] != "aridity" else "",
        ),
        subtitle=subtitle,
        titlefontsize=14,
    )
    cmap = get_cmap(ctx["cmap"])
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
    pvar = ctx["var"] + "_rank"
    fmt = "%.0f"
    if ctx["var"] == "aridity":
        bins = np.arange(-4, 4.1, 1)
        pvar = ctx["var"]
        fmt = "%.1f"
    mp.fill_climdiv(
        ctx["df"][pvar],
        ilabel=True,
        plotmissing=False,
        lblformat=fmt,
        bins=bins,
        cmap=cmap,
    )

    return mp.fig, ctx["df"]


if __name__ == "__main__":
    plotter(dict())
