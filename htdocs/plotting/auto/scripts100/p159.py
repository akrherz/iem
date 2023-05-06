"""
Based on available hourly observation reports
by METAR stations, this application presents the frequency of number
of hours for a given month or season at a given threshold.

<p>If you pick a custom day of the year period that crosses 1 January,
the year of the start date is used within the plot.</p>

<p><strong>Updated 18 Sep 2018:</strong>Plotting tool was updated
to consider dates prior to 1973 and to shade years that have more than
20% missing data.  The hourly averages are based on years with sufficient
data coverage.
"""
import datetime

import pandas as pd
from matplotlib.ticker import MaxNLocator
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

MDICT = {
    "all": "No Month/Time Limit",
    "custom": "Custom/Pick Start + End Date",
    "ytd": f"Jan 1 through {datetime.date.today():%b %-d}",
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
    "relh": "Relative Humidity (%)",
    "sped": "Wind Speed (mph)",
}
UNITS = {
    "tmpf": "F",
    "dwpf": "F",
    "feel": "F",
    "relh": "%",
    "sped": "mph",
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
            label="Threshold (F or % or MPH):",
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
            default=f"{datetime.date.today():%m%d}",
            label="Inclusive End Day of Year (when Date Limiter is custom):",
        ),
        dict(
            type="year",
            min=1973,
            default=datetime.date.today().year,
            label="Year to Highlight",
            name="year",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    month = ctx["month"]
    varname = ctx["var"]
    mydir = ctx["dir"]
    threshold = ctx["thres"]
    year = ctx["year"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]

    offset = "ts"
    mlabel = MDICT[month] if month != "jul1" else "Jul-Jun [year of Jul shown]"
    totaldays = 0
    months = range(1, 13)
    doylimit = ""
    if month in ["all", "jul1", "ytd"]:
        if month == "jul1":
            offset = "ts - '6 months'::interval"
    elif month == "custom":
        doylimit = (
            " and to_char(ts, 'mmdd') >= :sdate and "
            "to_char(ts, 'mmdd') <= :edate "
        )
        totaldays = (edate - sdate).days + 1
        mlabel = f" {sdate:%b %-d} thru {edate:%b %-d}"
        if sdate > edate:
            totaldays = (edate.replace(year=2001) - sdate).days + 1
            days = (edate - datetime.date(2000, 1, 1)).days + 1
            offset = f"ts - '{days} days'::interval"
            doylimit = (
                " and (to_char(ts, 'mmdd') >= :sdate or "
                "to_char(ts, 'mmdd') <= :edate) "
            )
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
        offset = "ts + '1 month'::interval"
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime(f"2000-{month}-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    opp = ">=" if mydir == "aoa" else "<"

    dbvarname = "(sknt * 1.15)" if varname == "sped" else varname
    if month == "ytd":
        doylimit = " and to_char(ts, 'mmdd') <= :sday "
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                f"""WITH hourly as (
            SELECT date_trunc('hour', valid + '10 minutes'::interval)
            at time zone :tzname as ts,
            case when {dbvarname}::int {opp} :t then 1 else 0 end as hit
            from alldata where station = :station and report_type = 3)

            SELECT extract(year from {offset})::int as year,
            extract(hour from ts)::int as hour,
            sum(hit) as hits, count(*) as obs from hourly
            WHERE extract(month from ts) in :months {doylimit}
            GROUP by year, hour
            """
            ),
            conn,
            params={
                "tzname": ctx["_nt"].sts[station]["tzname"],
                "t": threshold,
                "station": station,
                "months": tuple(months),
                "sday": datetime.date.today().strftime("%m%d"),
                "sdate": sdate.strftime("%m%d"),
                "edate": edate.strftime("%m%d"),
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    ydf = df.groupby("year").sum()
    title = (
        f"({mlabel}) {METRICS[varname]} Hours {DIRS[mydir]} "
        f"{threshold}{UNITS[varname]}\n"
        f"{ctx['_sname']}:: ({ydf.index.min():.0f}-{ydf.index.max():.0f})"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    ax[0].bar(
        ydf.index.values, ydf["hits"], align="center", fc="green", ec="green"
    )
    # Loop over plot years and background highlight any years with less than
    # 80% data coverage
    obscount = len(months) * 30 * 24 * 0.8
    if month == "ytd":
        obscount = int(f"{datetime.date.today():%j}") * 24 * 0.8
    elif month == "custom":
        obscount = totaldays * 24 * 0.8
    for _year in range(ydf.index.values[0], ydf.index.values[-1] + 1):
        if _year not in ydf.index or ydf.at[_year, "obs"] < obscount:
            ax[0].axvspan(_year - 0.5, _year + 0.5, color="#cfebfd", zorder=-3)
    if year in ydf.index.values:
        val = ydf.loc[year]
        ax[0].bar(
            year,
            val["hits"],
            align="center",
            fc="orange",
            ec="orange",
            zorder=5,
        )
    ax[0].grid(True)
    ax[0].set_ylabel("Hours")
    ax[0].set_xlim(ydf.index.min() - 0.5, ydf.index.max() + 0.5)
    ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax[0].set_xlabel("Years with blue shading have more than 20% missing data")
    avgv = ydf["hits"].mean()
    ax[0].axhline(avgv, color="k", zorder=10)
    ax[0].text(ydf.index.max() + 0.7, avgv, f"Avg\n{avgv:.1f}", va="center")

    df2 = ydf[ydf["obs"] > obscount]
    years = len(df2.index)
    df2 = df[df["year"].isin(df2.index.values)]
    hdf = df2.groupby("hour").sum() / years
    ax[1].bar(
        hdf.index.values,
        hdf["hits"],
        align="center",
        fc="b",
        ec="b",
        label="Avg",
    )
    thisyear = df[df["year"] == year]
    if not thisyear.empty:
        ax[1].bar(
            thisyear["hour"].values,
            thisyear["hits"],
            align="center",
            width=0.25,
            zorder=5,
            fc="orange",
            ec="orange",
            label=f"{year}",
        )
    ax[1].set_xlim(-0.5, 23.5)
    ax[1].grid(True)
    ax[1].legend(loc=(0.7, -0.22), ncol=2, fontsize=10)
    ax[1].set_ylabel("Days Per Period")
    ax[1].set_xticks(range(0, 24, 4))
    ax[1].set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax[1].set_xlabel(
        f"Hour of Day ({ctx['_nt'].sts[station]['tzname']})", ha="right"
    )
    return fig, df


if __name__ == "__main__":
    plotter(
        dict(
            network="CT_ASOS",
            zstation="GON",
            var="dwpf",
            thres=60,
            month="sep",
        )
    )
