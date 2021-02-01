"""accumulated precip."""
import datetime

from pandas.io.sql import read_sql
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound

PDICT = {
    "precip": "Precipitation",
    "snow": "Snow",
}


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

    <p>You can specify the start date (ignore the year) for when to start
    the 365 day accumulation of precipitation.  The year shown is the year
    for the start of the accumulation period.  For example, if you accumulate
    after 1 October, the year 2020 would represent the period from 1 Oct 2020
    to 30 Sep 2021.</p>

    <p>Accumulating snowfall data is frought with peril, but this app will let
    you do it!  The app has a tight requirement of no less than 3 days of
    missing data for the year to be considered in the plot.</p>
    """
    today = datetime.date.today()
    thisyear = today.year
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
            options=PDICT,
            name="var",
            default="precip",
            label="Accumulate Precipitation or Snow?",
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
        dict(
            optional=True,
            type="date",
            name="edate",
            default=f"2000/{today.strftime('%m/%d')}",
            min="2000/01/01",
            max="2000/12/31",
            label="End Day of Year for Plot: (ignore year)",
        ),
        dict(
            type="int",
            default="3",
            label="Number of missing days to allow before excluding year",
            name="m",
        ),
    ]
    return desc


def cull_missing(df, colname, missingdays):
    """Figure out which years need to go from the analysis."""
    df2 = df[["binyear", colname]]
    nancounts = df2.groupby("binyear").agg(lambda x: x.isnull().sum())
    # cull anything with more than 3 days NaN
    df2 = nancounts[nancounts[colname] > missingdays]
    years = []
    if not df2.empty:
        years = list(df2.index.values)
    return df[~df["binyear"].isin(years)], years


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
    # belt and suspenders
    assert ctx["var"] in PDICT
    df = read_sql(
        f"""
        with obs as (
            SELECT day, {ctx["var"]},
            case when sday >= %s then year else year - 1 end as binyear
            from {table} WHERE station = %s
        )
        SELECT day, binyear::int, {ctx["var"]},
        row_number() OVER (PARTITION by binyear ORDER by day ASC) as row,
        sum({ctx["var"]}) OVER (PARTITION by binyear ORDER by day ASC) as accum
        from obs ORDER by day ASC
    """,
        pgconn,
        params=(sdate.strftime("%m%d"), station),
        index_col="day",
    )
    if df.empty:
        raise NoDataFound("No data found!")
    # Truncate plot
    doy_trunc = 365
    today = ctx.get("edate", datetime.date.today())
    if ctx.get("edate") is not None:
        today_doy = int(today.strftime("%j"))
        sdate_doy = int(sdate.strftime("%j"))
        offset = 0 if today_doy > sdate_doy else 365
        doy_trunc = today_doy + offset - sdate_doy
        df = df[df["row"] <= doy_trunc]

    df, cullyears = cull_missing(df, ctx["var"], ctx["m"])

    extra = "" if doy_trunc == 365 else f" till {today.strftime('%-d %B')}"
    title = "Accumulated %s after %s%s" % (
        sdate.strftime("%-d %B"),
        PDICT[ctx["var"]],
        extra,
    )
    subtitle = "[%s] %s (%s-%s)" % (
        station,
        ctx["_nt"].sts[station]["name"],
        df["binyear"].min(),
        datetime.date.today().year,
    )
    if cullyears:
        subtitle += (
            f", {len(cullyears)} years excluded due to "
            f"missing > {ctx['m']} days"
        )

    (fig, ax) = figure_axes(title=title, subtitle=subtitle)
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
            df["binyear"][df["accum"].idxmax()],
            df["binyear"][df[df["row"] == doy_trunc]["accum"].idxmin()],
            year1,
            year2,
            year3,
        ],
        ["b", "brown", "r", "g", "purple"],
    ):
        if year is None or year in plotted:
            continue
        plotted.append(year)
        df2 = df[df["binyear"] == year]
        if df2.empty:
            continue
        lastrow = df2.iloc[-1]
        extra = ""
        if (lastrow["row"] + 2) < doy_trunc:
            extra = f" to {df2.index.values[-1].strftime('%-d %b')}"
        labelyear = year
        if df2.index.values[0].year != df2.index.values[-1].year:
            labelyear = "%s-%s" % (
                df2.index.values[0].year,
                df2.index.values[-1].year,
            )
        ax.plot(
            range(1, len(df2.index) + 1),
            df2["accum"],
            label="%s - %.2f%s" % (labelyear, lastrow["accum"], extra),
            color=color,
            lw=2,
        )

    ax.set_ylabel(PDICT[ctx["var"]] + " [inch]")
    ax.grid(True)
    ax.legend(loc=2)
    xticks = []
    xticklabels = []
    for i in range(doy_trunc + 1):
        date = sdate + datetime.timedelta(days=i)
        if date.day != 1:
            continue
        xticks.append(i)
        xticklabels.append(date.strftime("%b"))
    ax.set_xlim(0, doy_trunc + 1)
    ax.set_ylim(bottom=-0.1)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    return fig, df


if __name__ == "__main__":
    plotter(dict(sdate="2000-07-01", station="IA8706", var="snow"))
