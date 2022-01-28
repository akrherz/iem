"""max temp before jul 1 or min after"""
import datetime
import calendar

import psycopg2.extras
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "fall": "Minimum Temperature after 1 July",
    "spring": "Maximum Temperature for Year to Date",
}
PDICT2 = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the climatology and actual
    year's progression of warmest to date or coldest to date temperature.
    The simple average is presented along with the percentile intervals. When
    plotting the after 1 July period, the calendar year of the fall season
    is shown.  For example, 1 Jul 2019 to 30 Jun 2020 is 2019 for this plot."""
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
            name="year",
            default=datetime.datetime.now().year,
            label="Year (of fall season) to highlight:",
        ),
        dict(
            type="select",
            name="half",
            default="fall",
            label="Option to Plot:",
            options=PDICT,
        ),
        dict(
            type="select",
            name="var",
            default="low",
            label="Variable to Plot:",
            options=PDICT2,
        ),
        dict(type="int", name="t", label="Highlight Temperature", default=32),
    ]
    return desc


def get_context(fdict):
    """Get the raw infromations we need"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    today = datetime.date.today()
    thisyear = today.year
    ctx = get_autoplot_context(fdict, get_description())
    year = ctx["year"]
    station = ctx["station"]
    varname = ctx["var"]
    half = ctx["half"]
    table = "alldata_%s" % (station[:2],)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    startyear = int(ab.year)
    data = np.ma.ones((thisyear - startyear + 1, 366)) * 199
    if half == "fall":
        cursor.execute(
            f"""SELECT
            CASE WHEN month < 7 then
            extract(doy from day) + 366 else
            extract(doy from day) end,
            CASE WHEN month < 7 then year - 1 else year end, {varname}, day
            from {table} WHERE station = %s and low is not null and
            high is not null and day >= %s ORDER by day ASC""",
            (station, datetime.date(startyear, 7, 1)),
        )
    else:
        cursor.execute(
            f"""SELECT extract(doy from day), year, {varname} from
            {table} WHERE station = %s and high is not null and
            low is not null and year >= %s ORDER by day ASC""",
            (station, startyear),
        )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    subval = 1 if half == "spring" else 183
    for row in cursor:
        data[int(row[1] - startyear), int(row[0] - subval)] = row[2]

    data.mask = np.where(data == 199, True, False)

    doys = []
    avg = []
    p25 = []
    p2p5 = []
    p75 = []
    p97p5 = []
    mins = []
    maxs = []
    dyear = []
    idx = year - startyear
    doys = list(range(1, 366))
    f = np.ma.max if half == "spring" else np.ma.min
    lastdoy = int(today.strftime("%j"))
    if half == "fall" and today.month > 6:
        lastdoy -= 183
    for doy in doys:
        if year != today.year or doy < lastdoy:
            dyear.append(f(data[idx, :doy]))
        vals = f(data[:-1, :doy], 1)
        avg.append(np.ma.average(vals))
        mins.append(np.ma.min(vals))
        maxs.append(np.ma.max(vals))
        p = np.percentile(vals, [2.5, 25, 75, 97.5])
        p2p5.append(p[0])
        p25.append(p[1])
        p75.append(p[2])
        p97p5.append(p[3])

    # http://stackoverflow.com/questions/19736080
    d = dict(
        doy=pd.Series(doys) + subval,
        mins=pd.Series(mins),
        maxs=pd.Series(maxs),
        p2p5=pd.Series(p2p5),
        p97p5=pd.Series(p97p5),
        p25=pd.Series(p25),
        p75=pd.Series(p75),
        avg=pd.Series(avg),
        thisyear=pd.Series(dyear),
    )
    df = pd.DataFrame(d)
    addval = int(df["doy"].values[0] - 1)
    sts = datetime.date(2000, 1, 1) + datetime.timedelta(days=addval)
    df["dates"] = pd.date_range(sts, periods=len(doys))
    df = df.set_index("doy")
    ctx["df"] = df
    ctx["year"] = year
    ctx["half"] = half
    if ctx["half"] == "fall":
        title = "Minimum Daily %s Temperature after 1 July"
    else:
        title = "Maximum Daily %s Temperature"
    title = title % (varname.capitalize(),)
    ctx["ylabel"] = title
    ctx["title"] = "%s-%s %s %s\n%s" % (
        startyear,
        thisyear - 1,
        station,
        ctx["_nt"].sts[station]["name"],
        title,
    )
    return ctx


def highcharts(fdict):
    """Do highcharts"""
    ctx = get_context(fdict)

    rng = ctx["df"][["dates", "mins", "maxs"]].to_json(orient="values")
    p95 = ctx["df"][["dates", "p2p5", "p97p5"]].to_json(orient="values")
    p50 = ctx["df"][["dates", "p25", "p75"]].to_json(orient="values")
    mean = ctx["df"][["dates", "avg"]].to_json(orient="values")
    try:
        thisyear = ctx["df"][["dates", "thisyear"]].to_json(orient="values")
    except Exception:
        thisyear = "[]"
    return (
        """
$("#ap_container").highcharts({
    title: {text: '"""
        + ctx["title"].replace("\n", " ")
        + """'},
    tooltip: {shared: true,
        xDateFormat: '%B %d'},
    xAxis: {type: 'datetime',
        dateTimeLabelFormats: {
            day: '%b %e',
            week: '%b %e',
            month: '%b %e'}},
    yAxis: {title: {text: '"""
        + ctx["ylabel"]
        + """'}},
    series: [{
        name: 'Range',
        type: 'arearange',
        color: 'pink',
        tooltip: {valueDecimals: 0},
        data: """
        + rng
        + """
    },{
        name: '95th',
        type: 'arearange',
        color: 'tan',
        tooltip: {valueDecimals: 2},
        data: """
        + p95
        + """
    },{
        name: '50th',
        type: 'arearange',
        color: 'gold',
        tooltip: {valueDecimals: 2},
        data: """
        + p50
        + """
    },{
        name: 'Average',
        type: 'line',
        color: 'black',
        tooltip: {valueDecimals: 2},
        data: """
        + mean
        + """
    },{
        name: '"""
        + str(ctx["year"])
        + """',
        type: 'line',
        color: 'blue',
        tooltip: {valueDecimals: 0},
        shadow: {'color': 'white'},
        data: """
        + thisyear
        + """
    }]
});
    """
    )


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)
    df = ctx["df"]

    (fig, ax) = figure_axes(title=ctx["title"], apctx=ctx)
    doys = df.index.values
    ax.fill_between(
        doys, df["mins"], df["maxs"], color="pink", zorder=1, label="Range"
    )
    ax.fill_between(
        doys, df["p2p5"], df["p97p5"], color="tan", zorder=2, label="95 tile"
    )
    ax.fill_between(
        doys, df["p25"], df["p75"], color="gold", zorder=3, label="50 tile"
    )
    a = ax.plot(doys, df["avg"], zorder=4, color="k", lw=2, label="Average")
    series = df["thisyear"].dropna()
    ax.plot(
        series.index.values, series.values, color="white", lw=3.5, zorder=5
    )
    b = ax.plot(
        series.index.values,
        series.values,
        color="b",
        lw=1.5,
        zorder=6,
        label="%s" % (ctx["year"],),
    )
    if ctx["half"] == "spring":
        ax.set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
        ax.set_xticklabels(calendar.month_abbr[1:])
    if ctx["half"] == "fall":
        ax.set_xticks(
            np.array([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
            + 183
        )
        labels = calendar.month_abbr[7:]
        labels.extend(calendar.month_abbr[1:7])
        ax.set_xticklabels(labels)
    ax.set_ylabel(r"%s $^\circ$F" % (ctx["ylabel"],))
    ax.axhline(ctx["t"], linestyle="--", lw=1, color="k", zorder=6)
    ax.text(
        ax.get_xlim()[1], ctx["t"], r"%.0f$^\circ$F" % (ctx["t"],), va="center"
    )
    ax.grid(True)

    r = Rectangle((0, 0), 1, 1, fc="pink")
    r2 = Rectangle((0, 0), 1, 1, fc="tan")
    r3 = Rectangle((0, 0), 1, 1, fc="gold")

    loc = 1 if ctx["half"] == "fall" else 4
    ax.legend(
        [r, r2, r3, a[0], b[0]],
        [
            "Range",
            "95$^{th}$ %tile",
            "50$^{th}$ %tile",
            "Average",
            f"{ctx['year']}",
        ],
        loc=loc,
    )

    return fig, df


if __name__ == "__main__":
    highcharts(dict(network="IACLIMATE", station="IA0200", half="fall"))
