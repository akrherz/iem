"""Hourly temperature averages"""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
from scipy import stats
from matplotlib.font_manager import FontProperties
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict([("avg_tmpf", "Average Temperature")])
UNITS = {"avg_tmpf": "F"}
MDICT = OrderedDict(
    [
        ("all", "No Month Limit"),
        ("spring", "Spring (MAM)"),
        ("fall", "Fall (SON)"),
        ("winter", "Winter (DJF)"),
        ("summer", "Summer (JJA)"),
        ("gs", "1 May to 30 Sep"),
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


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents an average hourly value for
    a given month or season over the years covering the period of record
    for the site.  For the year to plot, at least 80% data availability needs
    to be obtained.
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
            name="month",
            default="all",
            options=MDICT,
            label="Select Month/Season/All",
        ),
        dict(
            type="hour",
            name="hour",
            default=20,
            label="At Time (Local Timezone of Station):",
        ),
        dict(
            type="select",
            name="var",
            options=PDICT,
            default="avg_tmpf",
            label="Which Variable to Plot",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    font0 = FontProperties()
    font0.set_family("monospace")
    font0.set_size(16)

    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())
    varname = ctx["var"]
    month = ctx["month"]
    station = ctx["zstation"]
    hour = ctx["hour"]

    if month == "all":
        months = range(1, 13)
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    else:
        ts = datetime.datetime.strptime("2000-" + month + "-01", "%Y-%b-%d")
        # make sure it is length two for the trick below in SQL
        months = [ts.month]

    df = read_sql(
        """
    WITH obs as (
        SELECT (valid + '10 minutes'::interval) at time zone %s as ts,
        tmpf::int as itmpf, dwpf::int as idwpf from alldata
        where station = %s and tmpf is not null
        and dwpf is not null and
        extract(month from valid at time zone %s) in %s),
    agg1 as (
        SELECT date_trunc('hour', ts) as hts, avg(itmpf) as avg_itmpf,
        avg(idwpf) as avg_idwpf from obs
        WHERE extract(hour from ts) = %s GROUP by hts)

    SELECT extract(year from hts)::int as year, avg(avg_itmpf) as avg_tmpf,
    count(*) as cnt
    from agg1 GROUP by year ORDER by year ASC
    """,
        pgconn,
        params=(
            ctx["_nt"].sts[station]["tzname"],
            station,
            ctx["_nt"].sts[station]["tzname"],
            tuple(months),
            hour,
        ),
        index_col="year",
    )
    if df.empty:
        raise NoDataFound("No data was found.")
    minfreq = len(months) * 30 * 0.8
    df2 = df[df["cnt"] > minfreq]
    lts = datetime.datetime(2000, 1, 1, int(hour), 0)
    title = "%s [%s] %s Local %s-%s" % (
        ctx["_nt"].sts[station]["name"],
        station,
        lts.strftime("%-I %p"),
        df2.index.min(),
        df2.index.max(),
    )
    subtitle = "%s [%s]" % (PDICT[varname], MDICT[month])
    (fig, ax) = figure_axes(title=title, subtitle=subtitle)
    ax.bar(df2.index.values, df2[varname], align="center", ec="b", fc="b")
    m = df2[varname].mean()
    ax.axhline(m, lw=2, zorder=5, color="k")
    slp, intercept, r, _, _ = stats.linregress(
        df2.index.values, df2[varname].values
    )
    ax.plot(
        df2.index.values,
        intercept + (df2.index.values * slp),
        color="r",
        lw=2,
        zorder=6,
    )
    ax.text(
        0.02,
        0.92,
        r"$\frac{^\circ}{decade} = %.2f,R^2=%.2f, avg = %.1f$"
        % (slp * 10.0, r ** 2, m),
        va="bottom",
        transform=ax.transAxes,
        bbox=dict(color="white"),
    )

    ax.set_ylim([df2[varname].min() - 5, df2[varname].max() + 5])
    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter(dict(month="08", network="IA_ASOS"))
