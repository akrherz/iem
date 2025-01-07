"""
This plot presents the observed frequency of
some daily event happening.  Leap day (Feb 29th) is excluded from the
analysis. If you download the data from this application, a placeholder
date during the year 2001 is used.</p>

<p>You can specify a given number of forward days to look for the given
threshold to happen.  Please be sure to review the aggregate function that
you want used over this period of days.
"""

from datetime import date, timedelta

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from sqlalchemy import text

from iemweb.autoplot import ARG_STATION

PDICT = {
    "high": "High Temp (F)",
    "low": "Low Temp (F)",
    "precip": "Precip (inch)",
    "snow": "Snowfall (inch)",
    "snowd": "Snow Depth (inch)",
}
PDICT2 = {
    "gte": "Greater than or equal to {threshold}",
    "lt": "Less than {threshold}",
    "rng": "Between Inclusive {threshold} and {threshold2}",
}
XREF = {"gte": ">=", "lt": "<"}
PDICT3 = {
    "min": "Minimum",
    "avg": "Average",
    "max": "Maximum",
    "sum": "Accumulated",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="year",
            name="syear",
            default=1893,
            min=1893,
            label="Start year for plot",
        ),
        dict(
            type="year",
            name="eyear",
            default=date.today().year,
            min=1893,
            label="End year (inclusive) for plot",
        ),
        dict(
            type="select",
            name="var",
            default="snow",
            label="Select Variable:",
            options=PDICT,
        ),
        dict(
            type="int",
            name="days",
            default="1",
            label="Number of Days to Look:",
        ),
        dict(
            options=PDICT3,
            type="select",
            name="f",
            default="avg",
            label="Statistical Aggregate Function over Number of Days",
        ),
        dict(
            type="select",
            name="opt",
            default="gte",
            label="Threshold Requirement:",
            options=PDICT2,
        ),
        dict(
            type="float", name="threshold", default="0.1", label="Threshold:"
        ),
        {
            "type": "float",
            "name": "threshold2",
            "default": 0.2,
            "label": "Threshold2 (when range is selected) (inclusive value)",
        },
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    params = {"station": station, "syear": ctx["syear"], "eyear": ctx["eyear"]}
    threshold = ctx["threshold"]
    threshold2 = ctx["threshold2"]
    params["threshold"] = threshold
    varname = ctx["var"]
    if ctx["opt"] == "rng":
        if threshold > threshold2:
            threshold, threshold2 = threshold2, threshold
        params["threshold"] = threshold
        params["threshold2"] = threshold2
        sql = "val >= :threshold and val <= :threshold2"
        vv = (
            PDICT2[ctx["opt"]]
            .replace("{threshold}", str(threshold))
            .replace("{threshold2}", str(threshold2))
        )
        subtitle = f"Frequency of {PDICT[varname]} {vv}"
    else:
        sql = f"val::numeric {XREF[ctx['opt']]} :threshold"
        vv = PDICT2[ctx["opt"]].replace("{threshold}", str(threshold))
        subtitle = f"Frequency of {PDICT[varname]} {vv} "
    if varname in ["high", "low"]:
        params["threshold"] = int(threshold)
        params["threshold2"] = int(threshold2)
    days = int(ctx["days"])
    func = "avg" if days == 1 else ctx["f"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            (
                text(
                    f"""
                WITH data as (
                SELECT sday, {func}({varname})
                OVER (ORDER by day ASC ROWS between
                CURRENT ROW and {days - 1} FOLLOWING) as val, day from alldata
                WHERE station = :station and {varname} is not null and
                year >= :syear and year <= :eyear)
                SELECT sday, sum(case when {sql} then 1 else 0
                end) as hits, count(*) as total,
                min(day) as min_date, max(day) as max_date from data
                WHERE sday != '0229' GROUP by sday ORDER by sday ASC
            """
                )
            ),
            conn,
            params=params,
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Covert sday into year 2001 date
    df["date"] = pd.to_datetime(df["sday"] + "2001", format="%m%d%Y")
    df = df.set_index("date")
    # calculate the frequency
    df["freq"] = df["hits"] / df["total"] * 100.0

    title = (
        f"{ctx['_sname']} "
        f"({df['min_date'].min().year}-{df['max_date'].max().year})"
    )
    if days > 1:
        subtitle += f" {PDICT3[func]} over inclusive forward {days} days"
    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    ax.bar(df.index.values, df["freq"], ec="b", fc="b")
    ax.set_xlim(
        df.index.min() - timedelta(days=1),
        df.index.max() + timedelta(days=1),
    )
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.grid(True)
    ax.set_ylabel("Frequency [%]")
    df = df.drop(columns=["min_date", "max_date"])
    return fig, df
