"""Daily Frequency of Some Threshold."""
from collections import OrderedDict
import datetime

import matplotlib.dates as mdates
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("high", "High Temp (F)"),
        ("low", "Low Temp (F)"),
        ("precip", "Precip (inch)"),
        ("snow", "Snowfall (inch)"),
        ("snowd", "Snow Depth (inch)"),
    ]
)
PDICT2 = OrderedDict(
    [("gte", "Greater than or equal to"), ("lt", "Less than")]
)
XREF = {"gte": ">=", "lt": "<"}
PDICT3 = {
    "min": "Minimum",
    "avg": "Average",
    "max": "Maximum",
    "sum": "Accumulated",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["cache"] = 86400
    desc["data"] = True
    desc[
        "description"
    ] = """This plot presents the observed frequency of
    some daily event happening.  Leap day (Feb 29th) is excluded from the
    analysis. If you download the data from this application, a placeholder
    date during the year 2001 is used.</p>

    <p>You can specify a given number of forward days to look for the given
    threshold to happen.  Please be sure to review the aggregate function that
    you want used over this period of days."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            network="IACLIMATE",
            default="IATDSM",
            label="Select Climate Site:",
        ),
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
            default=datetime.date.today().year,
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
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    threshold = ctx["threshold"]
    varname = ctx["var"]
    opt = XREF[ctx["opt"]]
    days = int(ctx["days"])
    table = "alldata_%s" % (station[:2],)
    func = "avg" if days == 1 else ctx["f"]

    df = read_sql(
        (
            "WITH data as ( "
            f"SELECT sday, {func}({varname}) "
            "OVER (ORDER by day ASC ROWS between "
            f"CURRENT ROW and {days - 1} FOLLOWING) as val, day from {table} "
            f"WHERE station = %s and {varname} is not null and year >= %s "
            "and year <= %s) "
            f"SELECT sday, sum(case when val {opt} {threshold} then 1 else 0 "
            "end) as hits, count(*) as total, "
            "min(day) as min_date, max(day) as max_date from data "
            "WHERE sday != '0229' GROUP by sday ORDER by sday ASC"
        ),
        pgconn,
        params=(station, ctx["syear"], ctx["eyear"]),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    # Covert sday into year 2001 date
    df["date"] = pd.to_datetime(df["sday"] + "2001", format="%m%d%Y")
    df.set_index("date", inplace=True)
    # calculate the frequency
    df["freq"] = df["hits"] / df["total"] * 100.0

    title = (
        f"{station} {ctx['_nt'].sts[station]['name']} "
        f"({df['min_date'].min().year}-{df['max_date'].max().year})"
    )
    subtitle = (
        f"Frequency of {PDICT[varname]} {PDICT2[ctx['opt']]} {threshold}"
    )
    if days > 1:
        subtitle += f" {PDICT3[func]} over inclusive forward {days} days"
    (fig, ax) = figure_axes(title=title, subtitle=subtitle)
    ax.bar(df.index.values, df["freq"], ec="b", fc="b")
    ax.set_xlim(
        df.index.min() - datetime.timedelta(days=1),
        df.index.max() + datetime.timedelta(days=1),
    )
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.grid(True)
    ax.set_ylabel("Frequency [%]")
    df.drop(["min_date", "max_date"], axis=1, inplace=True)
    return fig, df


if __name__ == "__main__":
    plotter(dict())
