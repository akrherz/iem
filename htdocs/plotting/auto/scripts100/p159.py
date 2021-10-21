"""Frequencies"""
import datetime
from collections import OrderedDict

from matplotlib.ticker import MaxNLocator
from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound

MDICT = OrderedDict(
    [
        ("all", "No Month/Time Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("jan", "January"),
        ("feb", "February"),
        ("mar", "March"),
        ("apr", "April"),
        ("may", "May"),
        ("jun", "June"),
        ("jul", "July"),
        ("aug", "August"),
        ("sep", "September"),
        ("oct", "October"),
        ("nov", "November"),
        ("dec", "December"),
    ]
)

METRICS = OrderedDict(
    [
        ("tmpf", "Air Temp (F)"),
        ("dwpf", "Dew Point Temp (F)"),
        ("feel", "Feels Like Temp (F)"),
        ("relh", "Relative Humidity (%)"),
    ]
)

DIRS = OrderedDict([("aoa", "At or Above"), ("below", "Below")])


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """Based on available hourly observation reports
    by METAR stations, this application presents the frequency of number
    of hours for a given month or season at a given threshold.

    <br /><br /><strong>Updated 18 Sep 2018:</strong>Plotting tool was updated
    to consider dates prior to 1973 and to shade years that have more than
    20% missing data.  The hourly averages are based on years with sufficient
    data coverage.
    """
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
            default="dwpf",
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
        dict(type="int", name="thres", default=65, label="Threshold (F or %)"),
        dict(
            type="select",
            name="month",
            default="all",
            label="Month Limiter",
            options=MDICT,
        ),
        dict(
            type="year",
            min=1973,
            default=datetime.date.today().year,
            label="Year to Highlight",
            name="year",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["zstation"]
    month = ctx["month"]
    varname = ctx["var"]
    mydir = ctx["dir"]
    threshold = ctx["thres"]
    year = ctx["year"]

    offset = "ts"
    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
        offset = "ts + '1 month'::interval"
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    opp = ">=" if mydir == "aoa" else "<"
    df = read_sql(
        f"""WITH hourly as (
        SELECT date_trunc('hour', valid + '10 minutes'::interval)
        at time zone %s as ts,
        max(case when {varname}::int {opp} %s then 1 else 0 end) as hit
        from alldata where station = %s and report_type = 2
        GROUP by ts)

        SELECT extract(year from {offset})::int as year,
        extract(hour from ts)::int as hour,
        sum(hit) as hits, count(*) as obs from hourly
        WHERE extract(month from ts) in %s GROUP by year, hour
        """,
        pgconn,
        params=(
            ctx["_nt"].sts[station]["tzname"],
            threshold,
            station,
            tuple(months),
        ),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("Error, no results returned!")

    (fig, ax) = plt.subplots(2, 1, figsize=(8, 6))
    ydf = df.groupby("year").sum()
    ax[0].set_title(
        ("(%s) %s Hours %s %s%s\n" "%s [%s] (%.0f-%.0f)")
        % (
            MDICT[month],
            METRICS[varname],
            DIRS[mydir],
            threshold,
            "%" if varname == "relh" else "F",
            ctx["_nt"].sts[station]["name"],
            station,
            ydf.index.min(),
            ydf.index.max(),
        )
    )
    ax[0].bar(
        ydf.index.values, ydf["hits"], align="center", fc="green", ec="green"
    )
    # Loop over plot years and background highlight any years with less than
    # 80% data coverage
    obscount = len(months) * 30 * 24 * 0.8
    for _year in range(ydf.index.values[0], ydf.index.values[-1] + 1):
        if _year not in ydf.index or ydf.at[_year, "obs"] < obscount:
            ax[0].axvspan(_year - 0.5, _year + 0.5, color="#cfebfd", zorder=-3)
    if year in ydf.index.values:
        val = ydf.loc[year]
        ax[0].bar(
            year,
            val["hits"],
            align="center",
            fc="orange",
            ec="orange",
            zorder=5,
        )
    ax[0].grid(True)
    ax[0].set_ylabel("Hours")
    ax[0].set_xlim(ydf.index.min() - 0.5, ydf.index.max() + 0.5)
    ax[0].xaxis.set_major_locator(MaxNLocator(integer=True))
    ax[0].set_xlabel("Years with blue shading have more than 20% missing data")

    df2 = ydf[ydf["obs"] > obscount]
    years = len(df2.index)
    df2 = df[df["year"].isin(df2.index.values)]
    hdf = df2.groupby("hour").sum() / years
    ax[1].bar(
        hdf.index.values,
        hdf["hits"],
        align="center",
        fc="b",
        ec="b",
        label="Avg",
    )
    thisyear = df[df["year"] == year]
    if not thisyear.empty:
        ax[1].bar(
            thisyear["hour"].values,
            thisyear["hits"],
            align="center",
            width=0.25,
            zorder=5,
            fc="orange",
            ec="orange",
            label="%s" % (year,),
        )
    ax[1].set_xlim(-0.5, 23.5)
    ax[1].grid(True)
    ax[1].legend(loc=(0.7, -0.22), ncol=2, fontsize=10)
    ax[1].set_ylabel("Days Per Period")
    ax[1].set_xticks(range(0, 24, 4))
    ax[1].set_xticklabels(["Mid", "4 AM", "8 AM", "Noon", "4 PM", "8 PM"])
    ax[1].set_xlabel(
        "Hour of Day (%s)" % (ctx["_nt"].sts[station]["tzname"],), ha="right"
    )
    return fig, df


if __name__ == "__main__":
    plotter(
        dict(
            network="CT_ASOS",
            zstation="GON",
            var="dwpf",
            thres=60,
            month="sep",
        )
    )
