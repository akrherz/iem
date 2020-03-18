"""jumps in temperature"""
import datetime
import calendar
from collections import OrderedDict

from pandas.io.sql import read_sql
from scipy import stats
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

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
MDICT = OrderedDict(
    [
        ("year", "All Year"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("gs", "Growing Season (May-Sep)"),
        ("1", "January"),
        ("2", "February"),
        ("3", "March"),
        ("4", "April"),
        ("5", "May"),
        ("6", "June"),
        ("7", "July"),
        ("8", "August"),
        ("9", "September"),
        ("10", "October"),
        ("11", "November"),
        ("12", "December"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This chart attempts to assess by now much the high temperature
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
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            label="Select Station:",
            network="IACLIMATE",
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
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    days = int(ctx["days"])
    fdays = int(ctx["fdays"])
    mdays = int(ctx["mdays"])
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

    table = "alldata_%s" % (station[:2],)

    obs = read_sql(
        """
     select day, extract(week from day) - 1 as week, year, month, sday,
     """
        + ctx["fstat"]
        + """("""
        + ctx["var"]
        + """) OVER
        (ORDER by day ASC rows between %s FOLLOWING and %s FOLLOWING)
        as forward_stat,
     """
        + ctx["fstat"]
        + """("""
        + ctx["var"]
        + """) OVER
        (ORDER by day ASC rows between CURRENT ROW and %s FOLLOWING)
        as middle_stat,
     """
        + ctx["stat"]
        + """("""
        + ctx["var"]
        + """) OVER
         (ORDER by day ASC rows between %s PRECEDING and 1 PRECEDING)
         as trailing_stat
     from """
        + table
        + """ where station = %s and month in %s ORDER by day ASC
    """,
        pgconn,
        params=(
            fdays,
            fdays + mdays - 1,
            fdays - 1,
            days,
            station,
            tuple(months),
        ),
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
        obs.at[down.index, "change"] = down[["two", "three"]].max(axis=1)
    else:
        obs["change"] = obs["two"]
    weekly = obs[[agg, "change"]].groupby(agg).describe()
    df = weekly["change"]

    extreme = max([df["max"].max(), 0 - df["min"].min()]) + 10

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.85, 0.65])
    multiplier = 1
    if agg == "week":
        multiplier = 7
        sts = datetime.datetime(2012, 1, 1)
        xticks = []
        for i in range(1, 13):
            ts = sts.replace(month=i)
            xticks.append(int(ts.strftime("%j")))

        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.set_xticks(xticks)
        ax.set_xlim(0, 366)
    elif agg == "month":
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.set_xticks(range(1, 13))
        ax.set_xlim(0, 13)
    elif agg == "year":
        for col in ["max", "min"]:
            h_slope, intercept, r_value, _, _ = stats.linregress(
                df.index.values, df[col]
            )
            y = h_slope * df.index.values + intercept
            ax.plot(df.index.values, y, lw=2, zorder=10, color="k")
            yloc = 2 if df[col].max() > 0 else -5
            color = "white" if yloc < 0 else "k"
            ax.text(
                df.index.values[-1],
                yloc,
                r"R^2=%.02f" % (r_value ** 2,),
                color=color,
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
    title = "Backward (%s) %.0f Days and Forward (%s) %.0f Inclusive Days" % (
        PDICT2[ctx["fstat"]],
        days,
        PDICT2[ctx["mstat"]],
        mdays,
    )
    if ctx["how"] == "three":
        title = ("Back (%s) %.0fd, Middle (%s) %.0fd, Forward (%s) %.0fd") % (
            PDICT2[ctx["fstat"]],
            days,
            PDICT2[ctx["mstat"]],
            mdays,
            PDICT2[ctx["fstat"]],
            fdays,
        )
    subtitle = (
        ""
        if ctx["thres"] is None
        else "\nBack Threshold of at least %.0f $^\circ$F" % (ctx["thres"],)
    )
    ax.set_title(
        ("%s %s\n" "Max Change in %s %s (%s)\n" "%s%s")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            PDICT3[ctx["var"]].replace("Temperature", "Temp"),
            PDICT[agg].replace("Aggregate", "Agg"),
            MDICT[month],
            title,
            subtitle,
        )
    )
    ax.set_ylim(0 - extreme, extreme)
    xloc = (ax.get_xlim()[1] + ax.get_xlim()[0]) / 2.0
    ax.text(
        xloc,
        extreme - 5,
        "Maximum Jump in %s (avg: %.1f)"
        % (PDICT3[ctx["var"]], df["max"].mean()),
        color="red",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )
    ax.text(
        xloc,
        0 - extreme + 5,
        "Maximum (Negative) Dip in %s (avg: %.1f)"
        % (PDICT3[ctx["var"]], df["min"].mean()),
        color="blue",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )

    return fig, df.rename({"datum": agg})


if __name__ == "__main__":
    plotter(dict(how="three"))
