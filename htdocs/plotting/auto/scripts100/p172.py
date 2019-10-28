"""accumulated precip."""
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot.use_agg import plt
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents year to date accumulated
    precipitation for a station of your choice.  The year with the highest and
    lowest accumulation is shown along with the envelop of observations and
    long term average.  You can optionally plot up to three additional years
    of your choice.</p>

    <p>You can specify the start date (ignore the year 2000) for when to start
    the 365 day accumulation of precipitation.  If you pick a date after
    1 July, the year plotted will represent the next calendar year.  For
    example picking the start date of 1 Oct 2000, the year 2020 plotted would
    represent the period 1 Oct 2019 thru 30 Sep 2020.  This is intended to
    emulate the water year nomenclature.
    """
    thisyear = datetime.date.today().year
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="year",
            name="year1",
            default=thisyear,
            label="Additional Year to Plot:",
        ),
        dict(
            type="year",
            name="year2",
            optional=True,
            default=(thisyear - 1),
            label="Additional Year to Plot: (optional)",
        ),
        dict(
            type="year",
            name="year3",
            optional=True,
            default=(thisyear - 2),
            label="Additional Year to Plot: (optional)",
        ),
        dict(
            type="date",
            name="sdate",
            default="2000/01/01",
            min="2000/01/01",
            max="2000/12/31",
            label="Start Day of Year for Plot: (ignore year)",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    year1 = ctx.get("year1")
    year2 = ctx.get("year2")
    year3 = ctx.get("year3")
    sdate = ctx["sdate"]
    table = "alldata_%s" % (station[:2],)
    delta = 1 if sdate.month > 6 else 0
    df = read_sql(
        """
        WITH years as (
            SELECT distinct year + %s as myyear from """
        + table
        + """
            WHERE station = %s and sday = %s),
        obs as (
            SELECT day, precip,
            case when sday >= %s then year + %s else year end as year
            from """
        + table
        + """ WHERE station = %s and precip is not null
        )
        SELECT day, year, precip,
        row_number() OVER (PARTITION by year ORDER by day ASC) as row,
        sum(precip) OVER (PARTITION by year ORDER by day ASC) as accum from
        obs WHERE year in (select myyear from years)
        ORDER by day ASC
    """,
        pgconn,
        params=(
            delta,
            station,
            sdate.strftime("%m%d"),
            sdate.strftime("%m%d"),
            delta,
            station,
        ),
        index_col="day",
    )
    if df.empty:
        raise NoDataFound("No data found!")

    (fig, ax) = plt.subplots(1, 1)
    # Average
    jday = df[["row", "accum"]].groupby("row").mean()
    jday["accum"].values[-1] = jday["accum"].values[-2]
    ax.plot(
        range(1, len(jday.index) + 1),
        jday["accum"],
        lw=2,
        zorder=5,
        color="k",
        label="Average - %.2f" % (jday["accum"].iloc[-1],),
    )

    # Min and Max
    jmin = df[["row", "accum"]].groupby("row").min()
    jmax = df[["row", "accum"]].groupby("row").max()
    ax.fill_between(
        range(1, len(jday.index) + 1),
        jmin["accum"],
        jmax["accum"],
        zorder=2,
        color="tan",
    )

    # find max year
    plotted = []
    for year, color in zip(
        [
            df["accum"].idxmax().year,
            df[df["row"] == 365]["accum"].idxmin().year,
            year1,
            year2,
            year3,
        ],
        ["b", "brown", "r", "g", "purple"],
    ):
        if year is None or year in plotted:
            continue
        plotted.append(year)
        df2 = df[df["year"] == year]
        ax.plot(
            range(1, len(df2.index) + 1),
            df2["accum"],
            label="%s - %.2f" % (year, df2["accum"].iloc[-1]),
            color=color,
            lw=2,
        )

    ax.set_title(
        ("Accumulated Precipitation after %s\n" "[%s] %s (%s-%s)")
        % (
            sdate.strftime("%-d %B"),
            station,
            ctx["_nt"].sts[station]["name"],
            ab.year,
            datetime.date.today().year,
        )
    )
    ax.set_ylabel("Precipitation [inch]")
    ax.grid(True)
    ax.legend(loc=2)
    xticks = []
    xticklabels = []
    for i in range(366):
        date = sdate + datetime.timedelta(days=i)
        if date.day != 1:
            continue
        xticks.append(i)
        xticklabels.append(date.strftime("%b"))
    ax.set_xlim(0, 367)
    ax.set_ylim(bottom=-0.1)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    return fig, df


if __name__ == "__main__":
    plotter(dict(sdate="2000-10-01"))
