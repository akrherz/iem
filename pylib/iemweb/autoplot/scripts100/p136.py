"""
This plot displays the number of accumulated
hours below a given wind chill temperature threshold by season. The
labeled season shown is for the year of January. So the season of 2016
would be from July 2015 to June 2016.  Hours with no wind are included
in this analysis with the wind chill temperature being the air temperature
in those instances.
"""

from datetime import date, datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context
from sqlalchemy import text

PDICT = {
    "0": "Include calm observations",
    "2": "Include only non-calm observations >= 2kt",
    "5": "Include only non-calm observations >= 5kt",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="year",
            name="season",
            default=datetime.now().year,
            label="Select Season to Highlight",
        ),
        dict(
            type="select",
            name="wind",
            default="0",
            options=PDICT,
            label="Include Calm Observations? (wind threshold)",
        ),
        dict(
            type="select",
            name="todate",
            default="no",
            options={"no": "No", "yes": "Yes"},
            label="Only consider season to date period?",
        ),
    ]
    return desc


def get_highcharts(ctx: dict) -> str:
    """Do highcharts"""
    add_ctx(ctx)
    season = ""
    if "season" in ctx["lines"]:
        season = (
            """{
        name: '"""
            + str(ctx["season"])
            + """',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""
            + ctx["lines"]["season"]["c"]
            + """'
        },
        data: """
            + str(
                [
                    list(a)
                    for a in zip(
                        ctx["lines"]["season"]["x"],
                        ctx["lines"]["season"]["y"],
                    )
                ]
            )
            + """

        },"""
        )
    d25 = str(
        [
            list(a)
            for a in zip(ctx["lines"]["25%"]["x"], ctx["lines"]["25%"]["y"])
        ]
    )
    dmean = str(
        [
            list(a)
            for a in zip(ctx["lines"]["mean"]["x"], ctx["lines"]["mean"]["y"])
        ]
    )
    d75 = str(
        [
            list(a)
            for a in zip(ctx["lines"]["75%"]["x"], ctx["lines"]["75%"]["y"])
        ]
    )
    dmax = str(
        [
            list(a)
            for a in zip(ctx["lines"]["max"]["x"], ctx["lines"]["max"]["y"])
        ]
    )
    containername = ctx["_e"]
    res = (
        """
Highcharts.chart('"""
        + containername
        + """', {
    title: {text: '"""
        + ctx["title"]
        + """'},
    subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
    chart: {zoomType: 'x'},
    tooltip: {
        shared: true,
        valueDecimals: 2,
        valueSuffix: ' days',
        headerFormat: '<span style="font-size: 10px">'+
                      'Wind Chill &lt;= {point.key} F</span><br/>'
    },
    xAxis: {title: {text: 'Wind Chill Temperature (F)'}},
    yAxis: {title: {text: 'Total Time Hours [expressed in days]'}},
    series: ["""
        + season
    )
    res += (
        """{
        name: '25%',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""
        + ctx["lines"]["25%"]["c"]
        + """'
        },
        data: """
        + d25
        + """
        },{
        name: 'Avg',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""
        + ctx["lines"]["mean"]["c"]
        + """'
        },
        data: """
        + dmean
        + """
        },{
        name: '75%',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""
        + ctx["lines"]["75%"]["c"]
        + """'
        },
        data: """
        + d75
        + """
        },{
        name: 'Max',
        type: 'line',
        marker: {
            lineWidth: 2,
            lineColor: '"""
        + ctx["lines"]["max"]["c"]
        + """'
        },
        data: """
        + dmax
        + """
        }]
});
    """
    )
    return res


def add_ctx(ctx):
    """Get the data"""
    station = ctx["zstation"]
    sknt = ctx["wind"]
    today = date.today()
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text("""
        WITH data as (
            SELECT valid, lag(valid) OVER (ORDER by valid ASC),
            extract(year from valid + '5 months'::interval) as season,
            wcht(tmpf::numeric, (sknt * 1.15)::numeric) from alldata
            WHERE station = :station and tmpf is not null and sknt is not null
            and tmpf < 50 and sknt >= :sknt and report_type = 3 ORDER by valid)
        SELECT case when (valid - lag) < '3 hours'::interval then (valid - lag)
        else '3 hours'::interval end as timedelta, wcht,
        season, to_char(valid, 'mmdd') as sday from data
        """),
            conn,
            params={"station": station, "sknt": sknt},
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data found for query.")
    textra = ""
    if ctx["todate"] == "yes":
        sday = today.strftime("%m%d")
        textra = f"till {today:%-d %b}"
        if sday < "0801":
            df = df[(df["sday"] < sday) | (df["sday"] > "0801")]
        else:
            df = df[(df["sday"] < sday) & (df["sday"] > "0801")]

    df2 = pd.DataFrame()
    for i in range(32, -51, -1):
        df2[i] = df[df["wcht"] < i].groupby("season")["timedelta"].sum()
    ctx["df"] = df2
    ctx["title"] = (
        f"{ctx['_sname']}:: Wind Chill Hours {textra} "
        f"({df['season'].min():.0f}-{df['season'].max():.0f})"
    )
    ctx["subtitle"] = f"Hours below threshold by season (wind >= {sknt} kts)"
    ctx["dfdescribe"] = df2.iloc[:-1].describe()
    ctx["season"] = int(ctx.get("season", datetime.now().year))
    ctx["lines"] = {}

    if ctx["season"] in ctx["df"].index.values:
        s = ctx["df"].loc[[ctx["season"]]].transpose()
        s = s.dropna().astype("timedelta64[s]")
        ctx["lines"]["season"] = {
            "x": s.index.values[::-1],
            "y": s[ctx["season"]].values[::-1] / 24.0 / 3600.0,
            "c": "blue",
            "label": f"{ctx['season']}",
        }
    lbls = ["25%", "mean", "75%", "max"]
    colors = ["g", "k", "r", "orange"]
    for color, lbl in zip(colors, lbls):
        s = ctx["dfdescribe"].loc[[lbl]].transpose()
        if s[lbl].isnull().all():
            continue
        s = s.dropna().astype("timedelta64[s]")
        ctx["lines"][lbl] = {
            "x": s.index.values[::-1],
            "y": s[lbl].values[::-1] / 24.0 / 3600.0,
            "label": lbl,
            "c": color,
        }
    if not ctx["lines"]:
        raise NoDataFound("No data found for query.")

    return ctx


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    add_ctx(ctx)

    (fig, ax) = figure_axes(
        apctx=ctx,
        title=f"{ctx['title']}\n{ctx['subtitle']}",
    )
    for year in ctx["df"].index.values:
        s = ctx["df"].loc[[year]].transpose()
        s = s.dropna().astype("timedelta64[s]")
        ax.plot(s.index.values, s[year].values / 24.0 / 3600.0, c="tan")
    if "season" in ctx["lines"]:
        ax.plot(
            ctx["lines"]["season"]["x"],
            ctx["lines"]["season"]["y"],
            c=ctx["lines"]["season"]["c"],
            zorder=5,
            label=ctx["lines"]["season"]["label"],
            lw=3,
        )
    for lbl in ["25%", "mean", "75%"]:
        if lbl not in ctx["lines"]:
            continue
        ax.plot(
            ctx["lines"][lbl]["x"],
            ctx["lines"][lbl]["y"],
            c=ctx["lines"][lbl]["c"],
            zorder=2,
            label=ctx["lines"][lbl]["label"],
            lw=2,
        )
    ax.legend(loc=2)
    ax.grid(True)
    ax.set_xlim(-50, 32)
    ax.set_xlabel(r"Wind Chill Temperature $^\circ$F")
    ax.set_ylabel("Total Time Hours [expressed in days]")
    return fig, ctx["df"]
