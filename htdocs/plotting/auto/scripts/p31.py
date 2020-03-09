"""jumps in temperature"""
import datetime
import calendar

from pandas.io.sql import read_sql
from scipy import stats
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"week": "Aggregate by Week of Year", "year": "Aggregate by Year"}
PDICT2 = {"min": "Minimum", "max": "Maximum", "avg": "Average"}
PDICT3 = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This chart attempts to assess by now much the high temperature
    can change between two periods of time.  These periods are defined by
    the consecutive number of days you choose.  The tricky part is to
    explain what exactly these periods are!  The forward period of days
    includes 'today', which is where this metric is evaluated.  So a forward
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
            type="int",
            name="fdays",
            default="1",
            label="Number of Forward Days (includes 'today'):",
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
    agg = ctx["agg"]
    # belt and suspenders
    assert agg in PDICT
    assert ctx["fstat"] in PDICT2
    assert ctx["stat"] in PDICT2
    assert ctx["var"] in PDICT3

    table = "alldata_%s" % (station[:2],)

    df = read_sql(
        """
    WITH data as (
     select day, extract(week from day) - 1 as week, year,
     """
        + ctx["fstat"]
        + """("""
        + ctx["var"]
        + """) OVER
        (ORDER by day ASC rows between CURRENT ROW and %s FOLLOWING)
        as forward_stat,
     """
        + ctx["stat"]
        + """("""
        + ctx["var"]
        + """) OVER
         (ORDER by day ASC rows between %s PRECEDING and 1 PRECEDING)
         as trailing_stat
     from """
        + table
        + """ where station = %s
    )
    SELECT """
        + agg
        + """ as datum,
    max(forward_stat - trailing_stat) as jump_up,
    min(forward_stat - trailing_stat) as jump_down
    from data GROUP by datum ORDER by datum ASC
    """,
        pgconn,
        params=(fdays - 1, days, station),
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    extreme = max([df["jump_up"].max(), 0 - df["jump_down"].min()]) + 10

    (fig, ax) = plt.subplots(1, 1)
    if agg == "week":
        sts = datetime.datetime(2012, 1, 1)
        xticks = []
        for i in range(1, 13):
            ts = sts.replace(month=i)
            xticks.append(int(ts.strftime("%j")))

        ax.bar(
            df["datum"].values * 7,
            df["jump_up"].values,
            width=7,
            fc="pink",
            ec="pink",
        )
        ax.bar(
            df["datum"].values * 7,
            df["jump_down"].values,
            width=7,
            fc="lightblue",
            ec="lightblue",
        )
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.set_xticks(xticks)
        ax.set_xlim(0, 366)
    elif agg == "year":
        ax.bar(df["datum"].values, df["jump_up"].values, fc="pink", ec="pink")
        ax.bar(
            df["datum"].values,
            df["jump_down"].values,
            fc="lightblue",
            ec="lightblue",
        )
        for col in ["jump_up", "jump_down"]:
            h_slope, intercept, r_value, _, _ = stats.linregress(
                df["datum"], df[col]
            )
            y = h_slope * df["datum"].values + intercept
            ax.plot(df["datum"].values, y, lw=2, zorder=10, color="k")
            yloc = 2 if df[col].max() > 0 else -5
            color = "white" if yloc < 0 else "k"
            ax.text(
                df["datum"].values[-1],
                yloc,
                r"R^2=%.02f" % (r_value ** 2,),
                color=color,
                ha="right",
            )
        ax.set_xlim(df["datum"].min() - 1, df["datum"].max() + 1)
    for col in ["jump_up", "jump_down"]:
        c = "red" if col == "jump_up" else "blue"
        ax.axhline(df[col].mean(), lw=2, color=c)

    ax.grid(True)
    ax.set_ylabel(r"Temperature Change $^\circ$F")
    ax.set_title(
        (
            "%s %s\n"
            "Max Change in %s %s\n"
            "Backward (%s) %.0f Days and Forward (%s) %.0f Inclusive Days"
        )
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            PDICT3[ctx["var"]],
            PDICT[agg],
            PDICT2[ctx["fstat"]],
            days,
            PDICT2[ctx["stat"]],
            fdays,
        )
    )
    ax.set_ylim(0 - extreme, extreme)
    xloc = (ax.get_xlim()[1] + ax.get_xlim()[0]) / 2.0
    ax.text(
        xloc,
        extreme - 5,
        "Maximum Jump in %s (avg: %.1f)"
        % (PDICT3[ctx["var"]], df["jump_up"].mean()),
        color="red",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )
    ax.text(
        xloc,
        0 - extreme + 5,
        "Maximum (Negative) Dip in %s (avg: %.1f)"
        % (PDICT3[ctx["var"]], df["jump_down"].mean()),
        color="blue",
        va="center",
        ha="center",
        bbox=dict(color="white"),
    )

    return fig, df.rename({"datum": agg})


if __name__ == "__main__":
    plotter(dict())
