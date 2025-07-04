"""
This plot presents a daily observation for a site
and year on a given date / holiday date each year.  A large caveat to this
chart is that much of the long term daily climate data is for a 24 hour
period ending at around 7 AM.  This chart will also not plot for dates
prior to the holiday's inception.
"""

import calendar
from datetime import date, datetime, timedelta

import pandas as pd
from dateutil.easter import easter as get_easter
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION
from iemweb.autoplot.barchart import barchart_with_top10

PDICT = {
    "easter": "Easter (Western Church Dates)",
    "labor": "Labor Day",
    "mlk": "Martin Luther King Day",
    "memorial": "Memorial Day",
    "mother": "Mothers Day",
    "exact": "Same Date each Year",
    "thanksgiving": "Thanksgiving",
}
PDICT2 = {
    "high": "High Temperature [F]",
    "low": "Low Temperature [F]",
    "precip": "Precipitation [inch]",
    "snow": "Snowfall [inch]",
    "snowd": "Snow Depth [inch]",
}
VARFORMAT = {
    "high": "%d",
    "low": "%d",
    "precip": "%.2f",
    "snow": "%.1f",
    "snowd": "%.1f",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        ARG_STATION,
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


def mlk():
    """MLK Day"""
    days = []
    for year in range(1986, date.today().year + 1):
        jan1 = date(year, 1, 1)
        if jan1.weekday() == 0:  # If Jan 1 is a Monday
            first_monday = jan1
        else:
            # Calculate the number of days until the next Monday
            days_until_monday = 7 - jan1.weekday()
            first_monday = jan1 + timedelta(days=days_until_monday)
        # Add 14 days to the first Monday to get the third Monday
        third_monday = first_monday + timedelta(days=14)
        days.append(third_monday)
    return days


def mothers_day():
    """Mother's Day"""
    days = []
    for year in range(1914, date.today().year + 1):
        may1 = date(year, 5, 1)
        days.append(date(year, 5, (14 - may1.weekday())))
    return days


def easter():
    """Compute easter"""
    return [get_easter(year) for year in range(1893, date.today().year + 1)]


def thanksgiving():
    """Thanksgiving please"""
    days = []
    # monday is 0
    offsets = [3, 2, 1, 0, 6, 5, 4]
    for year in range(1893, date.today().year + 1):
        nov1 = datetime(year, 11, 1)
        r1 = nov1 + timedelta(days=offsets[nov1.weekday()])
        days.append(r1 + timedelta(days=21))
    return days


def labor_days():
    """Labor Day Please"""
    days = []
    for year in range(1893, date.today().year + 1):
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
    for year in range(1971, date.today().year + 1):
        mycal = calendar.Calendar(0)
        cal = mycal.monthdatescalendar(year, 5)
        if cal[-1][0].month == 5:
            days.append(cal[-1][0])
        else:
            days.append(cal[-2][0])
    return days


def add_context(ctx):
    """Do the dirty work"""
    station = ctx["station"]
    ctx["varname"] = ctx["var"]
    thedate = ctx["thedate"]
    dt = ctx["date"]
    offset = ctx.get("offset")
    dtoff = None
    if offset is not None and -367 < offset < 367:
        dtoff = timedelta(days=offset)
        thedate = thedate + dtoff

    if dt == "exact":
        with get_sqlalchemy_conn("coop") as conn:
            ctx["df"] = pd.read_sql(
                sql_helper("""
    SELECT year, high, low, day, precip, snow, snowd, temp_hour, precip_hour
    from alldata WHERE station = :station and sday = :sday ORDER by year ASC
                """),
                conn,
                params={"station": station, "sday": thedate.strftime("%m%d")},
                index_col="year",
            )
        ctx["subtitle"] = thedate.strftime("%B %-d")
    else:
        if dt == "memorial":
            days = memorial_days()
        elif dt == "thanksgiving":
            days = thanksgiving()
        elif dt == "easter":
            days = easter()
        elif dt == "mother":
            days = mothers_day()
        elif dt == "mlk":
            days = mlk()
        else:
            days = labor_days()
        ctx["subtitle"] = PDICT[dt]
        if dtoff:
            ctx["subtitle"] = (
                f"{abs(offset)} Days {'before' if offset < 0 else 'after'} "
                f"{PDICT[dt]}"
            )
            days = [day + dtoff for day in days]
        with get_sqlalchemy_conn("coop") as conn:
            ctx["df"] = pd.read_sql(
                sql_helper("""
    SELECT year, high, day, low, precip, snow, snowd, temp_hour, precip_hour
    from alldata
    WHERE station = :station and day = ANY(:days) ORDER by year ASC
                """),
                conn,
                params={
                    "station": station,
                    "days": days,
                },
                index_col="year",
            )
    if ctx["df"].empty:
        raise NoDataFound("No Data Found.")
    ctx["title"] = f"{ctx['_sname']} :: Daily {PDICT2[ctx['varname']]}"


def get_highcharts(ctx: dict) -> str:
    """Generate javascript (Highcharts) variant"""
    add_context(ctx)
    ctx["df"] = ctx["df"].reset_index()
    v2 = ctx["df"][["year", ctx["varname"]]].to_json(orient="values")
    avgval = ctx["df"][ctx["varname"]].mean()
    avgvallbl = f"{avgval:.2f}"
    series = f"""{{
        name: '{ctx["varname"]}',
        data: {v2},
        color: '#0000ff'
    }}
    """

    containername = ctx["_e"]

    return f"""
    Highcharts.chart('{containername}', {{
        chart: {{
            type: 'column',
            zoomType: 'x'
        }},
        yAxis: {{
            title: {{text: '{PDICT2[ctx["varname"]]}'}},
            plotLines: [{{
                value: {avgval},
                color: 'green',
                dashStyle: 'shortdash',
                width: 2,
                zIndex: 5,
                label: {{
                    text: 'Average {avgvallbl}'
                }}
            }}]
        }},
        title: {{text: '{ctx["title"]}'}},
        subtitle: {{text: 'On {ctx["subtitle"]}'}},
        series: [{series}]
    }});
    """


def plotter(ctx: dict):
    """Go"""
    add_context(ctx)

    fig = figure(
        title=ctx["title"], subtitle=f"on {ctx['subtitle']}", apctx=ctx
    )
    ax = barchart_with_top10(
        fig,
        ctx["df"],
        ctx["varname"],
        labelformat=VARFORMAT[ctx["varname"]],
    )
    mean = ctx["df"][ctx["varname"]].mean()
    ax.axhline(mean)
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
    if ctx["varname"] not in ["precip", "snow", "snowd"]:
        ax.set_ylim(
            ctx["df"][ctx["varname"]].min() - 5,
            ctx["df"][ctx["varname"]].max() + 5,
        )

    # Denote contiguous years that have morning observations
    hrcol = "temp_hour" if ctx["varname"] in ["high", "low"] else "precip_hour"
    morning_obs_years = ctx["df"][ctx["df"][hrcol].isin(range(2, 12))].index

    # Group contiguous years
    contiguous_groups = []
    current_group = []

    for year in morning_obs_years:
        if not current_group or year == current_group[-1] + 1:
            current_group.append(year)
        else:
            contiguous_groups.append(current_group)
            current_group = [year]

    if current_group:
        contiguous_groups.append(current_group)

    # Plot contiguous year spans
    for group in contiguous_groups:
        ax.axvspan(
            group[0] - 0.49,
            group[-1] + 0.49,
            color="#0000ff",
            alpha=0.2,
            zorder=2,
        )
    if contiguous_groups:
        legend_elements = [
            Patch(
                facecolor="#0000ff",
                edgecolor="none",
                alpha=0.2,
                label="Morning Observations",
            )
        ]
        ax.legend(handles=legend_elements, loc="upper left")

    if ctx["varname"] == "snowd":
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        nonnull = ctx["df"][ctx["df"][ctx["varname"]].notnull()]
        if nonnull.empty:
            raise NoDataFound("No Snowdepth data for location.")
        oneinch = len(nonnull[nonnull["snowd"] > 1])
        percent = oneinch / len(nonnull) * 100.0
        ax.text(
            0.03,
            0.98,
            (
                f"{oneinch}/{len(nonnull)} ({percent:.1f}%) years "
                "with snow depth >= 1 inch"
            ),
            transform=ax.transAxes,
            va="top",
            ha="left",
            bbox=dict(facecolor="white", edgecolor="white"),
        )
    return fig, ctx["df"]
