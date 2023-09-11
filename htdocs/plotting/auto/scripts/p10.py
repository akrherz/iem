"""
This plot presents the period between the first
or last date for spring and fall season that the temperature was above or
below some threshold.  The year is split into two seasons on 1 July. A
simple linear trend line is placed on both dates.
"""
import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconnc
from scipy import stats

PDICT = {
    "above": "First Spring/Last Fall Temperature Above (>=) Threshold",
    "above2": "Last Spring/First Fall Temperature Above (>=) Threshold",
    "below": "Last Spring/First Fall Temperature Below Threshold",
}
PDICT2 = {
    "high": "High Temperature",
    "low": "Low Temperature",
    "snow": "Snowfall",
    "snowd": "Snow Cover Depth",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "report": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="direction",
            default="below",
            label="Threshold Direction",
            options=PDICT,
        ),
        dict(
            type="select",
            name="varname",
            default="low",
            label="Daily Variable to plot?",
            options=PDICT2,
        ),
        dict(
            type="float",
            name="threshold",
            default="32",
            label="Enter Threshold (degrees F or Inches):",
        ),
        dict(
            type="year", name="year", default=1893, label="Start Year of Plot"
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn, ccursor = get_dbconnc("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = ctx["threshold"]
    direction = ctx["direction"]
    varname = ctx["varname"]
    startyear = ctx["year"]

    if direction == "below":
        sql = f"""select year,
        max(case when {varname} < %s and month < 7
            then extract(doy from day) else 0 end) as spring,
        max(case when {varname} < %s and month < 7
            then day else null end) as spring_date,
        min(case when {varname} < %s and month > 6
            then extract(doy from day) else 388 end) as fall,
        min(case when {varname} < %s and month > 6
            then day else null end) as fall_date
        from alldata where station = %s
        GROUP by year ORDER by year ASC"""
    elif direction == "above":
        sql = f"""select year,
             min(case when {varname} >= %s and month < 7
                 then extract(doy from day) else 183 end) as spring,
             min(case when {varname} >= %s and month < 7
                 then day else null end) as spring_date,
             max(case when {varname} >= %s and month > 6
                 then extract(doy from day) else 183 end) as fall,
             max(case when {varname} >= %s and month > 6
                 then day else null end) as fall_date
            from alldata where station = %s
            GROUP by year ORDER by year ASC"""
    else:  # above2
        sql = f"""select year,
             max(case when {varname} >= %s and month < 7
                 then extract(doy from day) else 0 end) as spring,
             max(case when {varname} >= %s and month < 7
                 then day else null end) as spring_date,
             min(case when {varname} >= %s and month > 6
                 then extract(doy from day) else 388 end) as fall,
             min(case when {varname} >= %s and month > 6
                 then day else null end) as fall_date
            from alldata where station = %s
            GROUP by year ORDER by year ASC"""

    ccursor.execute(sql, (threshold, threshold, threshold, threshold, station))
    if ccursor.rowcount == 0:
        pgconn.close()
        raise NoDataFound("No Data Found.")
    rows = []
    for row in ccursor:
        if row["year"] < startyear:
            continue
        if row["fall"] > 366:
            continue
        if row["fall"] == 183 and row["spring"] == 183:
            continue
        rows.append(
            dict(
                year=row["year"],
                spring=row["spring"],
                fall=row["fall"],
                spring_date=row["spring_date"],
                fall_date=row["fall_date"],
            )
        )
    pgconn.close()
    df = pd.DataFrame(rows)
    if df.empty:
        raise NoDataFound("No data found for query.")
    df["season"] = df["fall"] - df["spring"]
    today = datetime.date.today()
    res = (
        "# IEM Climodat https://mesonet.agron.iastate.edu/climodat/\n"
        f"# Report Generated: {today:%d %b %Y}\n"
        f"# Climate Record: {ctx['_nt'].sts[station]['archive_begin']} "
        f"-> {today}\n"
        f"# Site Information: {ctx['_sname']}\n"
        "# Contact Information: Daryl Herzmann "
        "akrherz@iastate.edu 515.294.5978\n"
        f"# LENGTH OF SEASON FOR STATION NUMBER  {station}   "
        f"BASE TEMP={threshold}\n"
        "# LAST SPRING OCCURENCE FIRST FALL OCCURENCE\n"
        "   YEAR MONTH DAY DOY         MONTH DAY DOY   LENGTH OF SEASON\n"
    )
    for _, row in df.iterrows():
        if row["spring_date"] is None or row["fall_date"] is None:
            continue
        res += (
            f"{row['year']:7.0f}{row['spring_date'].month:4.0f}"
            f"{row['spring_date'].day:6.0f}{row['spring']:4.0f}        "
            f"{row['fall_date'].month:4.0f}{row['fall_date'].day:6.0f}"
            f"{row['fall']:4.0f}          {row['season']:.0f}\n"
        )
    sts = datetime.date(2000, 1, 1) + datetime.timedelta(
        days=df["spring"].mean()
    )
    ets = datetime.date(2000, 1, 1) + datetime.timedelta(
        days=df["fall"].mean()
    )
    res += (
        f"{'MEAN':7s}{sts.month:4.0f}{sts.day:6.0f}{df['spring'].mean():4.0f}"
        f"        {ets.month:4.0f}{ets.day:6.0f}{df['fall'].mean():4.0f}"
        f"          {df['season'].mean():.0f}\n"
    )
    years = np.array(df["year"], dtype=int)
    spring = np.array(df["spring"], dtype=int)
    fall = np.array(df["fall"], dtype=int)

    s_slp, s_int, s_r, _, _ = stats.linregress(years, spring)
    f_slp, f_int, f_r, _, _ = stats.linregress(years, fall)

    (fig, ax) = figure_axes(apctx=ctx)
    ax.bar(years, fall - spring, bottom=spring, ec="tan", fc="tan", zorder=1)
    for _v in [fall, spring]:
        avgv = int(np.average(_v))
        ts = datetime.date(2000, 1, 1) + datetime.timedelta(days=avgv - 1)
        ax.text(
            years[-1] + 3,
            avgv,
            ts.strftime("Avg:\n%-d %b"),
            ha="left",
            va="center",
        )
        ax.axhline(avgv, color="k")
    days = np.average(fall - spring)
    ax.text(
        1.02,
        0.5,
        f"<- {days:.1f} days ->",
        transform=ax.transAxes,
        rotation=-90,
    )
    ax.plot(
        years,
        years * s_slp + s_int,
        lw=3,
        zorder=2,
        label=(
            f"{(s_slp * 100.0):.2f} "
            r"$\frac{days}{100y}$ R$^2$="
            f"{(s_r**2):.2f}"
        ),
    )
    ax.plot(
        years,
        years * f_slp + f_int,
        lw=3,
        zorder=2,
        label=(
            f"{(f_slp * 100.0):.2f} "
            r"$\frac{days}{100y}$ R$^2$="
            f"{(f_r**2):.2f}"
        ),
    )
    ax.grid(True)
    title = PDICT.get(direction, "").replace(
        "Temperature", PDICT2.get(varname)
    )
    units = r"$^\circ$F" if not varname.startswith("snow") else "inch"
    ax.set_title(f"{ctx['_sname']}\n{title} {threshold}{units}")
    ax.legend(ncol=2, fontsize=14, labelspacing=2)
    ax.set_yticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax.set_yticklabels(calendar.month_abbr[1:])
    ax.set_ylim(min(spring) - 5, max(fall) + 30)
    ax.set_xlim(min(years) - 1, max(years) + 1)
    return fig, df, res


if __name__ == "__main__":
    plotter({})
