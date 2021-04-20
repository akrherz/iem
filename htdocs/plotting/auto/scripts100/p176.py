"""Besting previous record"""

import pandas as pd
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

PDICT = {"0": "Max Highs / Min Lows", "1": "Min Highs / Max Lows"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """
    This chart shows the margin by which new daily high
    and low temperatures set are beaten by.
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
    ]
    return desc


def get_context(fdict):
    """ Make the pandas Data Frame please"""
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
    dates = pd.date_range("2000/01/01", "2000/12/31").strftime("%m%d")
    if opt == "0":
        records = pd.DataFrame(dict(high=-9999, low=9999), index=dates)
        rows = []
        for row in cursor:
            if row[2] > records.at[row[1], "high"]:
                margin = row[2] - records.at[row[1], "high"]
                records.at[row[1], "high"] = row[2]
                if margin < 1000:
                    rows.append(dict(margin=margin, date=row[0]))
            if row[3] < records.at[row[1], "low"]:
                margin = row[3] - records.at[row[1], "low"]
                records.at[row[1], "low"] = row[3]
                if margin > -1000:
                    rows.append(dict(margin=margin, date=row[0]))
    else:
        records = pd.DataFrame(dict(high=9999, low=-9999), index=dates)
        rows = []
        for row in cursor:
            if row[2] < records.at[row[1], "high"]:
                margin = row[2] - records.at[row[1], "high"]
                records.at[row[1], "high"] = row[2]
                if margin > -1000:
                    rows.append(dict(margin=margin, date=row[0]))
            if row[3] > records.at[row[1], "low"]:
                margin = row[3] - records.at[row[1], "low"]
                records.at[row[1], "low"] = row[3]
                if margin < 1000:
                    rows.append(dict(margin=margin, date=row[0]))

    ctx["df"] = pd.DataFrame(rows)
    ctx["title"] = "[%s] %s Daily Record Margin" % (
        station,
        ctx["_nt"].sts[station]["name"],
    )
    ctx["subtitle"] = (
        "By how much did a new daily record beat the previous %s"
    ) % (PDICT[opt],)
    return ctx


def highcharts(fdict):
    """ Do highcharts option"""
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
    """ Go """
    ctx = get_context(fdict)

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))
    df2 = ctx["df"][ctx["df"]["margin"] > 0]
    ax.scatter(df2["date"].values, df2["margin"].values, color="r")

    df2 = ctx["df"][ctx["df"]["margin"] < 0]
    ax.scatter(df2["date"].values, df2["margin"].values, color="b")
    ax.set_ylim(-30, 30)
    ax.grid(True)
    ax.set_ylabel(r"Temperature Beat Margin $^\circ$F")
    ax.set_title("%s\n%s" % (ctx["title"], ctx["subtitle"]))

    return fig, ctx["df"]


if __name__ == "__main__":
    highcharts(dict())
