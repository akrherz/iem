"""autoplot ya'll"""
import calendar
import datetime

import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, convert_value
from pyiem.exceptions import NoDataFound

UNITS = {"mph": "miles per hour", "kt": "knots", "mps": "meters per second"}
UNITCONV = {"mph": "mile / hour", "kt": "knot", "mps": "meter / second"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This chart presents the hourly average wind speeds
    by month of the year or by custom periods.
    The hours presented are valid in the local time zone
    of the reporting station.  For example in Iowa, 3 PM would represent
    3 PM CDT in the summer and 3 PM CST in the winter.  Please complain to us
    if this logic causes you heartburn!  The format of the date periods is
    two digit month followed by two digit day for both the start and end
    date."""
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="select",
            name="units",
            default="mph",
            options=UNITS,
            label="Units of Average Wind Speed",
        ),
        dict(
            type="text",
            name="p1",
            optional=True,
            default="0501-0510",
            label="Optional. Average for inclusive period of days",
        ),
        dict(
            type="text",
            name="p2",
            optional=True,
            default="0511-0520",
            label="Optional. Average for inclusive period of days",
        ),
        dict(
            type="text",
            name="p3",
            optional=True,
            default="0521-0530",
            label="Optional. Average for inclusive period of days",
        ),
        dict(
            type="text",
            name="p4",
            optional=True,
            default="0601-0610",
            label="Optional. Average for inclusive period of days",
        ),
        dict(
            type="text",
            name="p5",
            optional=True,
            default="0611-0620",
            label="Optional. Average for inclusive period of days",
        ),
        dict(
            type="text",
            name="p6",
            optional=True,
            default="0621-0630",
            label="Optional. Average for inclusive period of days",
        ),
        dict(
            type="year",
            name="y1",
            optional=True,
            default=1973,
            label="Optional. Limit Period of Record to inclusive start year",
        ),
        dict(
            type="year",
            name="y2",
            optional=True,
            default=today.year,
            label="Optional. Limit Period of Record to inclusive end year",
        ),
    ]
    return desc


def get_context(fdict):
    """get context for both output types"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    ctx["station"] = station
    units = ctx["units"]
    p1 = ctx.get("p1")
    p2 = ctx.get("p2")
    p3 = ctx.get("p3")
    p4 = ctx.get("p4")
    p5 = ctx.get("p5")
    p6 = ctx.get("p6")
    y1 = ctx.get("y1")
    y2 = ctx.get("y2")

    ylimiter = ""
    if y1 is not None and y2 is not None:
        ylimiter = (
            f" and extract(year from valid) >= {y1} and "
            f"extract(year from valid) <= {y2} "
        )
    else:
        ab = ctx["_nt"].sts[station]["archive_begin"]
        if ab is None:
            raise NoDataFound("Unknown station metadata.")
        y1 = ab.year
        y2 = datetime.date.today().year

    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            f"""
        WITH obs as (
            SELECT (valid + '10 minutes'::interval) at time zone %s as ts,
            sknt from alldata where station = %s and sknt >= 0 and sknt < 150
            and report_type != 1 {ylimiter})

        select extract(month from ts)::int as month,
        extract(hour from ts)::int as hour, extract(day from ts)::int as day,
        avg(sknt) as avg_sknt from obs GROUP by month, day, hour
        ORDER by month, day, hour
            """,
            conn,
            params=(ctx["_nt"].sts[station]["tzname"], station),
            index_col=None,
        )
    # Figure out which mode we are going to do
    if all([a is None for a in [p1, p2, p3, p4, p5, p6]]):
        df = (
            df.drop(columns="day")
            .groupby(["month", "hour"])
            .mean()
            .reset_index()
        )
        ctx["ncols"] = 6
        ctx["labels"] = calendar.month_abbr
        ctx["subtitle"] = "Monthly Average Wind Speed by Hour"
    else:
        ctx["ncols"] = 3
        df["fake_date"] = pd.to_datetime(
            {"year": 2000, "month": df["month"], "day": df["day"]}
        )
        df = df.set_index("fake_date")
        dfs = []
        ctx["labels"] = [None]
        for p in [p1, p2, p3, p4, p5, p6]:
            if p is None:
                continue
            tokens = p.split("-")
            sts = datetime.datetime.strptime(
                "2000" + tokens[0].strip(), "%Y%m%d"
            )
            ets = datetime.datetime.strptime(
                "2000" + tokens[1].strip(), "%Y%m%d"
            )
            ldf = (
                df[["hour", "avg_sknt"]]
                .loc[sts.date() : ets.date()]
                .groupby("hour")
                .mean()
            )
            ldf = ldf.reset_index()
            ldf["month"] = len(dfs) + 1
            dfs.append(ldf)
            ctx["labels"].append(f"{sts:%b%d}-{ets:%b%d}")
            ctx["subtitle"] = "Period Average Wind Speed by Hour"
        df = pd.concat(dfs)

    df["avg_%s" % (units,)] = convert_value(
        df["avg_sknt"].values, "knot", UNITCONV[units]
    )
    ctx["df"] = df
    ctx["ylabel"] = "Average Wind Speed [%s]" % (UNITS[units],)
    ctx["xlabel"] = ("Hour of Day (timezone: %s)") % (
        ctx["_nt"].sts[station]["tzname"],
    )
    ctx["title"] = f"{ctx['_sname']} [{y1}-{y2}]"
    return ctx


def highcharts(fdict):
    """highcharts output"""
    ctx = get_context(fdict)
    lines = []
    for month, df2 in ctx["df"].groupby("month"):
        v = df2[["hour", "avg_" + ctx["units"]]].to_json(orient="values")
        lines.append(
            """{
            name: '"""
            + ctx["labels"][month]
            + """',
            type: 'line',
            tooltip: {valueDecimals: 1},
            data: """
            + v
            + """
            }
        """
        )
    series = ",".join(lines)
    return (
        """
    $("#ap_container").highcharts({
        chart: {
            type: 'column'
        },
        xAxis: {categories: ['Mid', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon', '1 PM',
        '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM',
        '10 PM', '11 PM'],
            title: {text: '"""
        + ctx["xlabel"]
        + """'}},
        tooltip: {shared: true},
        yAxis: {title: {text: '"""
        + ctx["ylabel"]
        + """'}},
        title: {text: '"""
        + ctx["title"]
        + """'},
        subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
        series: ["""
        + series
        + """]
    });
    """
    )


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)
    (fig, ax) = figure_axes(
        apctx=ctx, title=ctx["title"], subtitle=ctx["subtitle"]
    )
    colors = [
        None,
        "k",
        "k",
        "r",
        "r",
        "b",
        "b",
        "tan",
        "tan",
        "purple",
        "purple",
        "brown",
        "brown",
    ]
    styles = ["-", "--"]
    for month, df2 in ctx["df"].groupby("month"):
        ax.plot(
            df2["hour"].values,
            df2["avg_%s" % (ctx["units"],)],
            label=ctx["labels"][month],
            lw=2,
            color=colors[month],
            linestyle=styles[month % 2],
        )
    ax.set_ylabel(ctx["ylabel"])
    ax.grid(True)
    ax.set_position([0.1, 0.25, 0.85, 0.65])
    ax.legend(
        ncol=ctx["ncols"],
        bbox_to_anchor=(0.5, -0.22),
        fontsize=10,
        loc="center",
    )
    ax.set_xlabel(ctx["xlabel"])
    ax.set_xticks(range(0, 24, 4))
    ax.set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax.set_xlim(0, 23)

    return fig, ctx["df"]


if __name__ == "__main__":
    plotter({})
