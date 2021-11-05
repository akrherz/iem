"""Besting previous record"""

import pandas as pd
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound

PDICT = {"0": "Max Highs / Min Lows", "1": "Min Highs / Max Lows"}
PDICT2 = {
    "daily": "New Daily Record",
    "monthly": "New Monthly Record",
    "yearly": "New Yearly Record",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """
    This chart shows the margin by which a new daily high
    and low temperatures record beat the previously set record.  Ties are not
    presented on this plot.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
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


def get_context(fdict):
    """Make the pandas Data Frame please"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    opt = ctx["opt"]
    table = "alldata_%s" % (station[:2],)
    cursor.execute(
        f"SELECT day, sday, high, low from {table} WHERE station = %s "
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
            key = row[0].strftime(aggint)
            if row[2] > records.at[key, "high"]:
                margin = row[2] - records.at[key, "high"]
                records.at[key, "high"] = row[2]
                if margin < 1000:
                    rows.append(dict(margin=margin, date=row[0]))
            if row[3] < records.at[key, "low"]:
                margin = row[3] - records.at[key, "low"]
                records.at[key, "low"] = row[3]
                if margin > -1000:
                    rows.append(dict(margin=margin, date=row[0]))
    else:
        records = pd.DataFrame(dict(high=9999, low=-9999), index=dates)
        rows = []
        for row in cursor:
            key = row[0].strftime(aggint)
            if row[2] < records.at[key, "high"]:
                margin = row[2] - records.at[key, "high"]
                records.at[key, "high"] = row[2]
                if margin > -1000:
                    rows.append(dict(margin=margin, date=row[0]))
            if row[3] > records.at[key, "low"]:
                margin = row[3] - records.at[key, "low"]
                records.at[key, "low"] = row[3]
                if margin < 1000:
                    rows.append(dict(margin=margin, date=row[0]))

    ctx["df"] = pd.DataFrame(rows)
    ctx["title"] = "[%s] %s %s Margin" % (
        station,
        ctx["_nt"].sts[station]["name"],
        PDICT2[ctx["w"]],
    )
    ctx[
        "subtitle"
    ] = f"By how much did a new record beat the previous {PDICT[opt]}"
    return ctx


def highcharts(fdict):
    """Do highcharts option"""
    ctx = get_context(fdict)
    ctx["df"]["date"] = pd.to_datetime(ctx["df"]["date"])
    df2 = ctx["df"][ctx["df"]["margin"] > 0]
    v = df2[["date", "margin"]].to_json(orient="values")
    df2 = ctx["df"][ctx["df"]["margin"] < 0]
    v2 = df2[["date", "margin"]].to_json(orient="values")
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
    return (
        """
    $("#ap_container").highcharts({
        time: {useUTC: true}, // needed since we are using dates here :/
        chart: {
            type: 'scatter',
            zoomType: 'x'
        },
        tooltip: {
            valueDecimals: 0,
            pointFormat: 'Date: <b>{point.x:%b %d, %Y}</b>' +
                          '<br/>Margin: <b>{point.y}</b><br/>'},
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
    ctx = get_context(fdict)

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


if __name__ == "__main__":
    highcharts({"station": "WATSEA", "network": "WACLIMATE", "w": "monthly"})
