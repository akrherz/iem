"""
This plot displays the total reported snowfall for
a period prior to a given date and then after the date for the winter
season.  When you select a date to split the winter season, the year
shown in the date can be ignored.
"""

from datetime import date

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="date",
            name="date",
            default="2015/12/25",
            min="2015/01/01",
            label="Split Season by Date: (ignore the year)",
        ),
    ]
    return desc


def get_data(ctx):
    """Get the data"""
    station = ctx["station"]
    dt = ctx["date"]
    jul1 = date(dt.year if dt.month > 6 else dt.year - 1, 7, 1)
    offset = int((dt - jul1).days)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        with obs as (
            select day,
            day -
            ((case when month > 6 then year else year - 1 end)||'-07-01')::date
            as doy,
            (case when month > 6 then year else year - 1 end) as eyear, snow
            from alldata where station = %s)

            SELECT eyear,
            sum(case when doy < %s then snow else 0 end) as before,
            sum(case when doy >= %s then snow else 0 end) as after,
            sum(snow) as total from obs
            GROUP by eyear ORDER by eyear ASC
        """,
            conn,
            params=(station, offset, offset),
            index_col="eyear",
        )
    df = df[df["total"] > 0]
    return df


def get_highcharts(ctx: dict) -> dict:
    """Highcharts Output"""
    dt = ctx["date"]
    df = get_data(ctx)

    j = {}
    j["title"] = {"text": f"{ctx['_sname']}:: Snowfall Totals"}
    j["subtitle"] = {"text": f"Before and After {dt:%-d %B}"}
    j["xAxis"] = {
        "title": {"text": f"Snowfall Total [inch] before {dt:%-d %B}"},
        "plotLines": [
            {
                "color": "red",
                "value": df["before"].mean(),
                "width": 1,
                "label": {"text": "%.1fin" % (df["before"].mean(),)},
                "zindex": 2,
            }
        ],
    }
    j["yAxis"] = {
        "title": {"text": f"Snowfall Total [inch] on or after {dt:%-d %B}"},
        "plotLines": [
            {
                "color": "red",
                "value": df["after"].mean(),
                "width": 1,
                "label": {"text": "%.1fin" % (df["after"].mean(),)},
                "zindex": 2,
            }
        ],
    }
    j["chart"] = {"zoomType": "xy", "type": "scatter"}
    rows = []
    for yr, row in df.iterrows():
        rows.append(
            dict(
                x=round(row["before"], 2),
                y=round(row["after"], 2),
                name=f"{yr}-{yr + 1}",
            )
        )
    j["series"] = [
        {
            "data": rows,
            "tooltip": {
                "headerFormat": "",
                "pointFormat": (
                    "<b>Season:</b> {point.name}<br />"
                    "Before: {point.x} inch<br />"
                    "After: {point.y} inch"
                ),
            },
        }
    ]
    return j


def plotter(ctx: dict):
    """Go"""
    dt = ctx["date"]
    df = get_data(ctx)
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    title = (
        f"{ctx['_sname']}:: Snowfall Totals\n"
        f"Prior to and after: {dt:%-d %B}"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.scatter(df["before"].values, df["after"].values)
    ax.set_xlim(left=-0.1)
    ax.set_ylim(bottom=-0.1)
    ax.set_xlabel(f"Snowfall Total [inch] Prior to {dt:%-d %b}")
    ax.set_ylabel(f"Snowfall Total [inch] On and After {dt:%-d %b}")
    ax.grid(True)
    ax.axvline(
        df["before"].mean(),
        color="r",
        lw=2,
        label="Before Avg: %.1f" % (df["before"].mean(),),
    )
    ax.axhline(
        df["after"].mean(),
        color="b",
        lw=2,
        label="After Avg: %.1f" % (df["after"].mean(),),
    )
    ax.legend(ncol=2, fontsize=12)
    return fig, df
