"""
This plot presents the climatology and actual
year's progression of warmest to date or coldest to date temperature.
The simple average is presented along with the percentile intervals. When
plotting the after 1 July period, the calendar year of the fall season
is shown.  For example, 1 Jul 2019 to 30 Jun 2020 is 2019 for this plot.
"""

import calendar
from contextlib import suppress
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from sqlalchemy.engine import Connection

from iemweb.autoplot import ARG_STATION

PDICT = {
    "fall": "Minimum Temperature after 1 July",
    "spring": "Maximum Temperature for Year to Date",
}
PDICT2 = {"high": "High Temperature", "low": "Low Temperature"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="year",
            name="year",
            default=datetime.now().year,
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


@with_sqlalchemy_conn("coop")
def add_ctx(ctx, conn: Connection | None = None):
    """Get the raw infromations we need"""
    today = date.today()
    thisyear = today.year
    year = ctx["year"]
    station = ctx["station"]
    varname = ctx["var"]
    half = ctx["half"]

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    startyear = int(ab.year)
    data = np.ma.ones((thisyear - startyear + 1, 366)) * 199
    if half == "fall":
        res = conn.execute(
            sql_helper(
                """SELECT
            day - (
                (case when month > 6 then year else year - 1 end)::text ||
                '-07-01')::date as dt,
            case when month > 6 then year else year - 1 end as yr, {varname}
            from alldata WHERE station = :station and low is not null and
            high is not null and day >= :sday ORDER by day ASC""",
                varname=varname,
            ),
            {"station": station, "sday": date(startyear, 7, 1)},
        )
    else:
        res = conn.execute(
            sql_helper(
                """SELECT extract(doy from day) - 1 as dt,
            year as yr, {varname} from
            alldata WHERE station = :station and high is not null and
            low is not null and year >= :syear ORDER by day ASC""",
                varname=varname,
            ),
            {"station": station, "syear": startyear},
        )
    if res.rowcount == 0:
        raise NoDataFound("No Data Found.")
    for row in res.mappings():
        data[int(row["yr"] - startyear), int(row["dt"])] = row[varname]
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
    for doy in doys:
        if not np.ma.is_masked(data[idx, doy]):
            dyear.append(f(data[idx, : (doy + 1)]))
        vals = f(data[:-1, :doy], 1)
        avg.append(np.ma.average(vals))
        mins.append(np.ma.min(vals))
        maxs.append(np.ma.max(vals))
        p = np.nanpercentile(np.ma.filled(vals, np.nan), [2.5, 25, 75, 97.5])
        p2p5.append(p[0])
        p25.append(p[1])
        p75.append(p[2])
        p97p5.append(p[3])
    # http://stackoverflow.com/questions/19736080
    d = dict(
        doy=pd.Series(doys) + (1 if half == "spring" else 183),
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
    sts = date(2000, 1, 1) + timedelta(days=addval)
    df["dates"] = pd.date_range(sts, periods=len(doys))
    df = df.set_index("doy")
    ctx["df"] = df
    ctx["year"] = year
    ctx["half"] = half
    if ctx["half"] == "fall":
        title = "Season to Date Minimum Daily %s Temperature after 1 July"
    else:
        title = "Year to Date Maximum Daily %s Temperature"
    title = title % (varname.capitalize(),)
    ctx["ylabel"] = title
    ctx["title"] = f"{startyear}-{thisyear - 1} {ctx['_sname']}\n{title}"
    return ctx


def get_highcharts(ctx: dict) -> str:
    """Do highcharts"""
    add_ctx(ctx)
    rng = ctx["df"][["dates", "mins", "maxs"]].to_json(
        orient="values", date_format="iso"
    )
    p95 = ctx["df"][["dates", "p2p5", "p97p5"]].to_json(
        orient="values", date_format="iso"
    )
    p50 = ctx["df"][["dates", "p25", "p75"]].to_json(
        orient="values", date_format="iso"
    )
    mean = ctx["df"][["dates", "avg"]].to_json(
        orient="values", date_format="iso"
    )
    thisyear = "[]"
    with suppress(Exception):
        thisyear = ctx["df"][["dates", "thisyear"]].to_json(
            orient="values", date_format="iso"
        )
    containername = ctx["_e"]
    title = ctx["title"].replace("\n", " ")
    return f"""
Highcharts.chart('{containername}', {{
    title: {{text: '{title}'}},
    tooltip: {{shared: true,
        xDateFormat: '%B %d'}},
    xAxis: {{type: 'datetime',
        dateTimeLabelFormats: {{
            day: '%b %e',
            week: '%b %e',
            month: '%b %e'}}}},
    yAxis: {{title: {{text: '{ctx["ylabel"]}'}}}},
    series: [{{
        name: 'Range',
        type: 'arearange',
        color: 'pink',
        tooltip: {{valueDecimals: 0}},
        data: {rng}
    }},{{
        name: '95th',
        type: 'arearange',
        color: 'tan',
        tooltip: {{valueDecimals: 2}},
        data: {p95}
    }},{{
        name: '50th',
        type: 'arearange',
        color: 'gold',
        tooltip: {{valueDecimals: 2}},
        data: {p50}
    }},{{
        name: 'Average',
        type: 'line',
        color: 'black',
        tooltip: {{valueDecimals: 2}},
        data: {mean}
    }},{{
        name: '{ctx["year"]}',
        type: 'line',
        color: 'blue',
        tooltip: {{valueDecimals: 0}},
        shadow: {{'color': 'white'}},
        data: {thisyear}
    }}]
}});
    """


def plotter(ctx: dict):
    """Go"""
    add_ctx(ctx)
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
        label=f"{ctx['year']}",
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
    ax.set_ylabel(f"{ctx['ylabel']} °F")
    ax.axhline(ctx["t"], linestyle="--", lw=1, color="k", zorder=6)
    ax.text(
        ax.get_xlim()[1],
        ctx["t"],
        f"{ctx['t']:.0f}°F",
        va="center",
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
