"""
This chart shows the margin by which a new daily high
and low temperatures record beat the previously set record.  Ties are not
presented on this plot.
"""

import pandas as pd
from pyiem.database import get_dbconnc
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context

from iemweb.autoplot import ARG_STATION

PDICT = {"0": "Max Highs / Min Lows", "1": "Min Highs / Max Lows"}
PDICT2 = {
    "daily": "New Daily Record",
    "monthly": "New Monthly Record",
    "yearly": "New Yearly Record",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="opt",
            default="0",
            options=PDICT,
            label="Which metric to plot",
        ),
        dict(
            type="select",
            name="w",
            default="daily",
            options=PDICT2,
            label="Compute records over which time interval",
        ),
    ]
    return desc


def add_context(ctx):
    """Make the pandas Data Frame please"""
    pgconn, cursor = get_dbconnc("coop")
    station = ctx["station"]
    opt = ctx["opt"]
    cursor.execute(
        "SELECT day, sday, high, low from alldata WHERE station = %s "
        "and high is not null and low is not null ORDER by day ASC",
        (station,),
    )
    if cursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    aggint = "%m%d"
    if ctx["w"] == "monthly":
        aggint = "%m"
    elif ctx["w"] == "yearly":
        aggint = "1"
    dates = pd.date_range("2000/01/01", "2000/12/31").strftime(aggint).unique()
    if opt == "0":
        records = pd.DataFrame(dict(high=-9999, low=9999), index=dates)
        rows = []
        for row in cursor:
            key = row["day"].strftime(aggint)
            if row["high"] > records.at[key, "high"]:
                margin = row["high"] - records.at[key, "high"]
                records.at[key, "high"] = row["high"]
                if margin < 1000:
                    rows.append(
                        dict(margin=margin, date=row["day"], val=row["high"])
                    )
            if row["low"] < records.at[key, "low"]:
                margin = row["low"] - records.at[key, "low"]
                records.at[key, "low"] = row["low"]
                if margin > -1000:
                    rows.append(
                        dict(margin=margin, date=row["day"], val=row["low"])
                    )
    else:
        records = pd.DataFrame(dict(high=9999, low=-9999), index=dates)
        rows = []
        for row in cursor:
            key = row["day"].strftime(aggint)
            if row["high"] < records.at[key, "high"]:
                margin = row["high"] - records.at[key, "high"]
                records.at[key, "high"] = row["high"]
                if margin > -1000:
                    rows.append(
                        dict(margin=margin, date=row["day"], val=row["high"])
                    )
            if row["low"] > records.at[key, "low"]:
                margin = row["low"] - records.at[key, "low"]
                records.at[key, "low"] = row["low"]
                if margin < 1000:
                    rows.append(
                        dict(margin=margin, date=row["day"], val=row["low"])
                    )
    pgconn.close()
    ctx["df"] = pd.DataFrame(rows)
    ctx["title"] = f"{ctx['_sname']} :: {PDICT2[ctx['w']]} Margin"
    ctx["subtitle"] = (
        f"By how much did a new record beat the previous {PDICT[opt]}"
    )


def get_highcharts(ctx: dict) -> str:
    """Do highcharts option"""
    add_context(ctx)
    ctx["df"]["date"] = pd.to_datetime(ctx["df"]["date"])
    df2 = ctx["df"][ctx["df"]["margin"] > 0]
    cols = ["date", "margin", "val"]
    rename = {"date": "x", "margin": "y"}
    v = df2[cols].rename(columns=rename).to_json(orient="records")
    df2 = ctx["df"][ctx["df"]["margin"] < 0]
    v2 = df2[cols].rename(columns=rename).to_json(orient="records")
    a = "High" if ctx["opt"] == "0" else "Low"
    b = "High" if ctx["opt"] == "1" else "Low"
    series = (
        """{
        data: """
        + v
        + """,
        color: '#ff0000',
        name: '"""
        + a
        + """ Temp Beat'
    },{
        data: """
        + v2
        + """,
        color: '#0000ff',
        name: '"""
        + b
        + """ Temp Beat'
    }
    """
    )
    containername = ctx["_e"]
    return (
        """
Highcharts.chart('"""
        + containername
        + """', {
        time: {useUTC: true}, // needed since we are using dates here :/
        chart: {
            type: 'scatter',
            zoomType: 'x'
        },
        plotOptions: {
            scatter: {
                turboThreshold: 0
            }
        },
        tooltip: {
            valueDecimals: 0,
            pointFormat: 'Date: <b>{point.x:%b %d, %Y}</b>' +
                          '<br/>Margin: <b>{point.y}</b>' +
                          '<br />Ob: <b>{point.val}</b>'},
        yAxis: {title: {text: 'Temperature Beat Margin F'}},
        xAxis: {type: 'datetime'},
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
    ctx = get_autoplot_context(fdict, get_description())
    add_context(ctx)

    (fig, ax) = figure_axes(
        title=ctx["title"], subtitle=ctx["subtitle"], apctx=ctx
    )
    df2 = ctx["df"][ctx["df"]["margin"] > 0]
    ax.scatter(df2["date"].values, df2["margin"].values, color="r")

    df2 = ctx["df"][ctx["df"]["margin"] < 0]
    ax.scatter(df2["date"].values, df2["margin"].values, color="b")
    ax.set_ylim(-30, 30)
    ax.grid(True)
    ax.set_ylabel(r"Temperature Beat Margin $^\circ$F")

    return fig, ctx["df"]
