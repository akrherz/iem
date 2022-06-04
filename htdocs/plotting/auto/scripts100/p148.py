"""Special Days each year"""
import datetime
import calendar

from dateutil.easter import easter as get_easter
import pandas as pd
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound
from sqlalchemy import text

PDICT = {
    "easter": "Easter (Western Church Dates)",
    "labor": "Labor Day",
    "memorial": "Memorial Day",
    "mother": "Mothers Day",
    "exact": "Same Date each Year",
    "thanksgiving": "Thanksgiving",
}
PDICT2 = {
    "high": "High Temperature [F]",
    "low": "Low Temperature [F]",
    "precip": "Precipitation [inch]",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot presents a daily observation for a site
    and year on a given date / holiday date each year.  A large caveat to this
    chart is that much of the long term daily climate data is for a 24 hour
    period ending at around 7 AM.  This chart will also not plot for dates
    prior to the holiday's inception.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0200",
            network="IACLIMATE",
            label="Select Station:",
        ),
        dict(
            type="select",
            name="date",
            default="memorial",
            options=PDICT,
            label="Which date/holiday to plot?",
        ),
        dict(
            type="sday",
            name="thedate",
            default="0101",
            label="Same date each year to plot (when selected above):",
        ),
        dict(
            type="int",
            optional=True,
            name="offset",
            default=1,
            label="Number of offset days from chosen date (minus is before)",
        ),
        dict(
            type="select",
            name="var",
            default="high",
            label="Which variable to plot?",
            options=PDICT2,
        ),
    ]
    return desc


def mothers_day():
    """Mother's Day"""
    days = []
    for year in range(1914, datetime.date.today().year + 1):
        may1 = datetime.date(year, 5, 1)
        days.append(datetime.date(year, 5, (14 - may1.weekday())))
    return days


def easter():
    """Compute easter"""
    return [
        get_easter(year)
        for year in range(1893, datetime.date.today().year + 1)
    ]


def thanksgiving():
    """Thanksgiving please"""
    days = []
    # monday is 0
    offsets = [3, 2, 1, 0, 6, 5, 4]
    for year in range(1893, datetime.date.today().year + 1):
        nov1 = datetime.datetime(year, 11, 1)
        r1 = nov1 + datetime.timedelta(days=offsets[nov1.weekday()])
        days.append(r1 + datetime.timedelta(days=21))
    return days


def labor_days():
    """Labor Day Please"""
    days = []
    for year in range(1893, datetime.date.today().year + 1):
        mycal = calendar.Calendar(0)
        cal = mycal.monthdatescalendar(year, 9)
        if cal[0][0].month == 9:
            days.append(cal[0][0])
        else:
            days.append(cal[1][0])
    return days


def memorial_days():
    """Memorial Day Please"""
    days = []
    for year in range(1971, datetime.date.today().year + 1):
        mycal = calendar.Calendar(0)
        cal = mycal.monthdatescalendar(year, 5)
        if cal[-1][0].month == 5:
            days.append(cal[-1][0])
        else:
            days.append(cal[-2][0])
    return days


def get_context(fdict):
    """Do the dirty work"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    ctx["varname"] = ctx["var"]
    thedate = ctx["thedate"]
    date = ctx["date"]
    offset = ctx.get("offset")
    dtoff = None
    if offset is not None and -367 < offset < 367:
        dtoff = datetime.timedelta(days=offset)
        thedate = thedate + dtoff

    table = f"alldata_{station[:2]}"
    if date == "exact":
        with get_sqlalchemy_conn("coop") as conn:
            ctx["df"] = pd.read_sql(
                f"SELECT year, high, day, precip from {table} "
                "WHERE station = %s and sday = %s ORDER by year ASC",
                conn,
                params=(station, thedate.strftime("%m%d")),
                index_col="year",
            )
        ctx["subtitle"] = thedate.strftime("%B %-d")
    else:
        if date == "memorial":
            days = memorial_days()
        elif date == "thanksgiving":
            days = thanksgiving()
        elif date == "easter":
            days = easter()
        elif date == "mother":
            days = mothers_day()
        else:
            days = labor_days()
        ctx["subtitle"] = PDICT[date]
        if dtoff:
            ctx["subtitle"] = (
                f"{abs(offset)} Days {'before' if offset < 0 else 'after'} "
                f"{PDICT[date]}"
            )
            days = [day + dtoff for day in days]
        with get_sqlalchemy_conn("coop") as conn:
            ctx["df"] = pd.read_sql(
                text(
                    f"SELECT year, high, day, precip from {table} "
                    "WHERE station = :station and day in :days "
                    "ORDER by year ASC"
                ),
                conn,
                params={
                    "station": station,
                    "days": tuple(days),
                },
                index_col="year",
            )
    if ctx["df"].empty:
        raise NoDataFound("No Data Found.")
    ctx["title"] = f"{ctx['_sname']} :: Daily {PDICT2[ctx['varname']]}"
    return ctx


def highcharts(fdict):
    """Generate javascript (Highcharts) variant"""
    ctx = get_context(fdict)
    ctx["df"] = ctx["df"].reset_index()
    v2 = ctx["df"][["year", ctx["varname"]]].to_json(orient="values")
    avgval = ctx["df"][ctx["varname"]].mean()
    avgvallbl = f"{avgval:.2f}"
    series = (
        """{
        name: '"""
        + ctx["varname"]
        + """',
        data: """
        + v2
        + """,
        color: '#0000ff'
    }
    """
    )

    return (
        """
    $("#ap_container").highcharts({
        chart: {
            type: 'column',
            zoomType: 'x'
        },
        yAxis: {
            title: {text: '"""
        + PDICT2[ctx["varname"]]
        + """'},
            plotLines: [{
                value: """
        + str(avgval)
        + """,
                color: 'green',
                dashStyle: 'shortdash',
                width: 2,
                zIndex: 5,
                label: {
                    text: 'Average """
        + avgvallbl
        + """'
                }
            }]
        },
        title: {text: '"""
        + ctx["title"]
        + """'},
        subtitle: {text: 'On """
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

    (fig, ax) = figure_axes(apctx=ctx)

    ax.bar(
        ctx["df"].index.values,
        ctx["df"][ctx["varname"]],
        fc="r",
        ec="r",
        align="center",
    )
    mean = ctx["df"][ctx["varname"]].mean()
    ax.axhline(mean)
    ax.set_title(f"{ctx['title']}\non {ctx['subtitle']}")
    ax.text(
        ctx["df"].index.values[-1] + 1,
        mean,
        f"{mean:.2f}",
        ha="left",
        va="center",
    )
    ax.grid(True)
    ax.set_xlim(
        ctx["df"].index.values.min() - 1, ctx["df"].index.values.max() + 1
    )
    ax.set_ylabel(PDICT2[ctx["varname"]])
    if ctx["varname"] != "precip":
        ax.set_ylim(
            ctx["df"][ctx["varname"]].min() - 5,
            ctx["df"][ctx["varname"]].max() + 5,
        )
    return fig, ctx["df"]


if __name__ == "__main__":
    plotter(dict(date="easter"))
