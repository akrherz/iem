"""
This application plots the number of days for a
given month or period of months that a given variable was above or below
some threshold.
"""
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

MDICT = {
    "all": "No Month/Time Limit",
    "spring": "Spring (MAM)",
    "fall": "Fall (SON)",
    "winter": "Winter (DJF)",
    "summer": "Summer (JJA)",
    "jan": "January",
    "feb": "February",
    "mar": "March",
    "apr": "April",
    "may": "May",
    "jun": "June",
    "jul": "July",
    "aug": "August",
    "sep": "September",
    "oct": "October",
    "nov": "November",
    "dec": "December",
}

METRICS = {
    "avg_sknt": "Avg Wind Speed (kts)",
    "max_sknt": "Max Wind Speed (kts)",
    "max_gust": "Max Wind Speed Gust (kts)",
    "max_tmpf": "Max Air Temp (F)",
    "min_tmpf": "Min Air Temp (F)",
    "max_dwpf": "Max Dew Point Temp (F)",
    "min_dwpf": "Min Dew Point Temp (F)",
    "max_feel": "Max Feels Like Temperature (F)",
    "avg_feel": "Avg Feels Like Temperature (F)",
    "min_feel": "Min Feels Like Temperature (F)",
    "max_rh": "Max Relative Humidity (%)",
    "avg_rh": "Avg Relative Humidity (%)",
    "min_rh": "Min Relative Humidity (%)",
    "pday": "Precipitation (inch)",
}

DIRS = {"aoa": "At or Above", "below": "Below"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="var",
            default="max_dwpf",
            label="Which Variable",
            options=METRICS,
        ),
        dict(
            type="select",
            name="dir",
            default="aoa",
            label="Threshold Direction:",
            options=DIRS,
        ),
        dict(type="int", name="thres", default=65, label="Threshold"),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="year",
            min=1928,
            default=datetime.date.today().year,
            label="Year to Highlight",
            name="year",
        ),
    ]
    return desc


def get_context(fdict):
    """Do the processing work"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    month = ctx["month"]
    varname = ctx["var"]
    mydir = ctx["dir"]
    threshold = ctx["thres"]

    offset = "day"
    if month == "all":
        months = list(range(1, 13))
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
        offset = "day + '1 month'::interval"
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month, 999]

    opp = ">=" if mydir == "aoa" else "<"
    with get_sqlalchemy_conn("iem") as conn:
        ctx["df"] = pd.read_sql(
            text(
                f"""
            SELECT extract(year from {offset})::int as year,
            sum(case when {varname}::int {opp} :t then 1 else 0 end) as count
            from summary s JOIN stations t on (s.iemid = t.iemid)
            WHERE t.id = :station and t.network = :network
            and extract(month from day) = ANY(:months)
            and {varname} is not null
            GROUP by year ORDER by year ASC
            """
            ),
            conn,
            params={
                "t": threshold,
                "station": station,
                "network": ctx["network"],
                "months": months,
            },
            index_col="year",
        )
    ctx["title"] = "(%s) %s %s %.0f" % (
        MDICT[ctx["month"]],
        METRICS[ctx["var"]],
        DIRS[ctx["dir"]],
        ctx["thres"],
    )
    ctx["subtitle"] = ctx["_sname"]
    return ctx


def highcharts(fdict):
    """Highcharts output"""
    ctx = get_context(fdict)
    ctx["df"] = ctx["df"].reset_index()
    data = ctx["df"][["year", "count"]].to_json(orient="values")
    containername = fdict.get("_e", "ap_container")

    return (
        """
Highcharts.chart('"""
        + containername
        + """', {
        chart: {
            type: 'column'
        },
        yAxis: {title: {text: 'Days'}},
        title: {text: '"""
        + ctx["title"]
        + """'},
        subtitle: {text: '"""
        + ctx["subtitle"]
        + """'},
        series: [{
            name: 'Days',
            data: """
        + data
        + """
        }]
    });
    """
    )


def plotter(fdict):
    """Go"""
    ctx = get_context(fdict)
    df = ctx["df"]
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    title = f"{ctx['title']}\n{ctx['subtitle']}"
    (fig, ax) = figure_axes(apctx=ctx, title=title)
    ax.bar(
        df.index.values, df["count"], align="center", fc="green", ec="green"
    )
    if ctx["year"] in df.index:
        ax.bar(
            ctx["year"],
            df.at[ctx["year"], "count"],
            align="center",
            fc="red",
            ec="red",
            zorder=5,
        )
    ax.grid(True)
    ax.set_ylabel("Days Per Period")
    ax.set_xlim(df.index.min() - 0.5, df.index.max() + 0.5)
    avgv = df["count"].mean()
    ax.axhline(avgv)
    ax.text(df.index.max() + 1, avgv, "%.1f" % (avgv,))
    return fig, df


if __name__ == "__main__":
    plotter({})
