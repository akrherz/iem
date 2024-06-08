"""
This chart attempts to assess by now much the high temperature
can change between two or three periods of time.
These periods are defined by
the consecutive number of days you choose.  The tricky part is to
explain what exactly these periods are!  The middle period of days
includes 'today', which is where this metric is evaluated.  So a middle
period of <code>1</code> days only includes 'today' and not 'tomorrow'.
If you summarize this plot by year, a simple linear trendline is
presented as well.

<p>A practical example here may be warranted.  Consider a period of
four days whereby the warmest high temperature was only 40 degrees F. Then
on the next day, the high temperature soars to 60 degrees.  For the plot
settings of <code>4</code> trailing days (Maxiumum)
and <code>1</code> forward days (Whatever, does not matter for 1 day
aggregate),
this example evaluates to a jump of 20 degrees.
"""

import calendar
import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from scipy import stats
from sqlalchemy import text

PDICT = {
    "month": "Aggregate by Month",
    "week": "Aggregate by Week of Year",
    "year": "Aggregate by Year",
}
PDICT2 = {"min": "Minimum", "max": "Maximum", "avg": "Average"}
PDICT3 = {"high": "High Temperature", "low": "Low Temperature"}
PDICT4 = {
    "two": "Just consider trailing and middle period",
    "three": "Consider full cycle between trailing, middle, and forward",
}
MDICT = {
    "year": "All Year",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "gs": "Growing Season (May-Sep)",
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
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="year",
            min=1893,
            default=1893,
            label="Start Year for Plot:",
            name="syear",
        ),
        dict(
            type="year",
            min=1893,
            default=datetime.date.today().year,
            label="End Year for Plot:",
            name="eyear",
        ),
        dict(
            type="select",
            name="month",
            default="year",
            label="Month/Season",
            options=MDICT,
        ),
        dict(
            type="select",
            name="how",
            default="two",
            label="Analyze two or three periods?",
            options=PDICT4,
        ),
        dict(
            type="select",
            name="var",
            default="high",
            label="Which variable to analyze:",
            options=PDICT3,
        ),
        dict(
            type="int",
            name="days",
            default="4",
            label="Number of Trailing Days (excludes 'today'):",
        ),
        dict(
            type="select",
            default="max",
            name="stat",
            options=PDICT2,
            label="Trailing Days Aggregation Function:",
        ),
        dict(
            optional=True,
            type="int",
            name="thres",
            label="Threshold temperature for trailing period (At or Above)",
            default=70,
        ),
        dict(
            type="int",
            name="mdays",
            default="1",
            label="Number of Days in Middle Period (includes 'today'):",
        ),
        dict(
            type="select",
            default="min",
            name="mstat",
            options=PDICT2,
            label="Middle Days Aggregation Function:",
        ),
        dict(
            type="int",
            name="fdays",
            default="1",
            label="Number of Days in Forward Period (following middle):",
        ),
        dict(
            type="select",
            default="min",
            name="fstat",
            options=PDICT2,
            label="Forward Days Aggregation Function:",
        ),
        dict(
            type="select",
            options=PDICT,
            default="week",
            name="agg",
            label="How to Aggregate the data?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = int(ctx["days"])
    fdays = int(ctx["fdays"])
    mdays = int(ctx["mdays"])
    syear = int(ctx["syear"])
    eyear = int(ctx["eyear"])
    agg = ctx["agg"]
    # belt and suspenders
    assert agg in PDICT
    assert ctx["fstat"] in PDICT2
    assert ctx["mstat"] in PDICT2
    assert ctx["stat"] in PDICT2
    assert ctx["var"] in PDICT3

    month = ctx["month"]
    months = list(range(1, 13))
    if month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    elif month != "year":
        months = [int(month)]
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            text(
                f"""WITH data as (
        select day, extract(week from day) - 1 as week, year, month, sday,
        {ctx["fstat"]}({ctx["var"]}) OVER
            (ORDER by day ASC rows between :f1 FOLLOWING and :f2 FOLLOWING)
            as forward_stat, {ctx["mstat"]}({ctx["var"]}) OVER
            (ORDER by day ASC rows between CURRENT ROW and :f3 FOLLOWING)
            as middle_stat, {ctx["stat"]}({ctx["var"]}) OVER
            (ORDER by day ASC rows between :days PRECEDING and 1 PRECEDING)
            as trailing_stat
        from alldata where station = :station)
        SELECT * from data WHERE month = ANY(:months) and year >= :syear
            and year <= :eyear ORDER by day ASC
        """
            ),
            conn,
            params={
                "f1": fdays,
                "f2": fdays + mdays - 1,
                "f3": fdays - 1,
                "days": days,
                "station": station,
                "months": months,
                "syear": syear,
                "eyear": eyear,
            },
        )
    if obs.empty:
        raise NoDataFound("No Data Found.")
    if ctx.get("thres") is not None:
        obs = obs[obs["trailing_stat"] >= ctx["thres"]]
        if obs.empty:
            raise NoDataFound("Failed to find events with trailing threshold")
    else:
        ctx["thres"] = None

    # We have daily observations above in the form of obs
    obs["two"] = obs["middle_stat"] - obs["trailing_stat"]
    obs["three"] = obs["middle_stat"] - obs["forward_stat"]
    if ctx["how"] == "three":
        up = obs[(obs["two"] >= 0) & (obs["three"] >= 0)]
        obs["change"] = up[["two", "three"]].min(axis=1)
        down = obs[(obs["two"] < 0) & (obs["three"] < 0)]
        obs.loc[down.index, "change"] = down[["two", "three"]].max(axis=1)
    else:
        obs["change"] = obs["two"]
    weekly = obs[[agg, "change"]].groupby(agg).describe()
    df = weekly["change"]

    extreme = max([df["max"].max(), 0 - df["min"].min()]) + 10
    title = (
        f"Backward ({PDICT2[ctx['stat']]}) {days:.0f} Days and Forward "
        f"({PDICT2[ctx['mstat']]}) {mdays:.0f} Inclusive Days"
    )
    if ctx["how"] == "three":
        title = (
            f"Back ({PDICT2[ctx['stat']]}) {days:.0f}d, Middle "
            f"({PDICT2[ctx['mstat']]}) {mdays:.0f}d, Forward "
            f"({PDICT2[ctx['fstat']]}) {fdays:.0f}d"
        )
    subtitle = (
        ""
        if ctx["thres"] is None
        else rf"\nBack Threshold of at least {ctx['thres']:.0f} $^\circ$F"
    )
    tt = syear
    if ctx["_nt"].sts[station]["archive_begin"] is not None:
        tt = max([ctx["_nt"].sts[station]["archive_begin"].year, syear])
    title = (
        f"{ctx['_sname']} ({tt:.0f}-{eyear:.0f}) Max Change in "
        f"{PDICT3[ctx['var']].replace('Temperature', 'Temp')} "
        f"{PDICT[agg].replace('Aggregate', 'Agg')} ({MDICT[month]})\n"
        f"{title}{subtitle}"
    )
    fig, ax = figure_axes(title=title, apctx=ctx)
    multiplier = 1
    if agg == "week":
        multiplier = 7
        sts = datetime.datetime(2012, 1, 1)
        xticks = []
        for i in range(1, 13):
            ts = sts.replace(month=i)
            xticks.append(int(ts.strftime("%j")))

        ax.set_xticks(xticks)
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.set_xlim(0, 366)
    elif agg == "month":
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.set_xlim(0, 13)
    elif agg == "year":
        for col in ["max", "min"]:
            h_slope, intercept, r_value, _, _ = stats.linregress(
                df.index.values, df[col]
            )
            y = h_slope * df.index.values + intercept
            ax.plot(df.index.values, y, lw=2, zorder=10, color="k")
            yloc = 0.55 if col == "max" else 0.45
            color = "white" if yloc < 0 else "k"
            ax.text(
                0.9,
                yloc,
                r"R^2=" f"{(r_value**2):.02f}",
                color=color,
                transform=ax.transAxes,
                va="center",
                ha="right",
            )
        ax.set_xlim(df.index.values[0] - 1, df.index.values[-1] + 1)
    ax.bar(
        df.index.values * multiplier,
        df["max"].values,
        width=multiplier,
        fc="pink",
        ec="pink",
    )
    ax.bar(
        df.index.values * multiplier,
        df["min"].values,
        width=multiplier,
        fc="lightblue",
        ec="lightblue",
    )
    for col in ["max", "min"]:
        c = "red" if col == "max" else "blue"
        ax.axhline(df[col].mean(), lw=2, color=c)

    ax.grid(True)
    ax.set_ylabel(r"Temperature Change $^\circ$F")
    ax.set_ylim(0 - extreme, extreme)
    xloc = (ax.get_xlim()[1] + ax.get_xlim()[0]) / 2.0
    ax.text(
        xloc,
        extreme - 5,
        f"Maximum Jump in {PDICT3[ctx['var']]} (avg: {df['max'].mean():.1f})",
        color="red",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )
    ax.text(
        xloc,
        0 - extreme + 5,
        f"Maximum (Negative) Dip in {PDICT3[ctx['var']]} "
        f"(avg: {df['min'].mean():.1f})",
        color="blue",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )

    return fig, df.rename({"datum": agg})


if __name__ == "__main__":
    plotter({})
