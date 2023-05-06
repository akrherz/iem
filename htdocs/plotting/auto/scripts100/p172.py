"""accumulated precip."""
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn

PDICT = {
    "precip": "Precipitation",
    "snow": "Snow",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
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
            type="sday",
            name="sdate",
            default="0101",
            label="Start Day of Year for Plot:",
        ),
        dict(
            optional=True,
            type="sday",
            name="edate",
            default=f"{today:%m%d}",
            label="End Day of Year for Plot:",
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
    resdf = df[~df["binyear"].isin(years)]
    minyear = resdf["binyear"].min()
    # Prevent scary cullyears listing
    return resdf, list(filter(lambda x: x > minyear, years))


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    year1 = ctx.get("year1")
    year2 = ctx.get("year2")
    year3 = ctx.get("year3")
    sdate = ctx["sdate"]
    # belt and suspenders
    assert ctx["var"] in PDICT
    with get_sqlalchemy_conn("coop") as conn:
        climo = pd.read_sql(
            """
            SELECT to_char(valid, 'mmdd') as sday, precip as cprecip,
            snow as csnow
            from ncei_climate91 where station = %s ORDER by sday
            """,
            conn,
            params=(ctx["_nt"].sts[station]["ncei91"],),
            index_col="sday",
        )
        df = pd.read_sql(
            f"""
            with obs as (
                SELECT day, {ctx["var"]}, sday,
                case when sday >= %s then year else year - 1 end as binyear
                from alldata WHERE station = %s
            )
            SELECT day, binyear::int, {ctx["var"]}, sday,
            row_number() OVER (PARTITION by binyear ORDER by day ASC) as row,
            sum({ctx["var"]}) OVER (PARTITION by binyear ORDER by day ASC)
                as accum
            from obs ORDER by day ASC
        """,
            conn,
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
    if not climo.empty:
        df = df.join(climo, how="left", on="sday")

    extra = "" if doy_trunc == 365 else f" through {today.strftime('%-d %B')}"
    title = f"Accumulated {PDICT[ctx['var']]}{extra} after {sdate:%-d %B}"
    subtitle = (
        f"{ctx['_sname']} ({df['binyear'].min()}-{datetime.date.today().year})"
    )
    if cullyears:
        subtitle += (
            f", {len(cullyears)} years excluded due to "
            f"missing > {ctx['m']} days"
        )

    (fig, ax) = figure_axes(title=title, subtitle=subtitle, apctx=ctx)
    # Average
    jday = df[["row", "accum"]].groupby("row").mean()
    jday["accum"].values[-1] = jday["accum"].values[-2]
    if climo.empty:
        ax.plot(
            range(1, len(jday.index) + 1),
            jday["accum"],
            lw=2,
            zorder=5,
            color="k",
            label=f"Simple Average - {jday['accum'].iloc[-1]:.2f}",
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
            labelyear = (
                f"{df2.index.values[0].year}-{df2.index.values[-1].year}"
            )
        ax.plot(
            range(1, len(df2.index) + 1),
            df2["accum"],
            label=f"{labelyear} - {lastrow['accum']:.2f}{extra}",
            color=color,
            lw=2,
        )
    # NCEI91 Climatology
    if not climo.empty:
        df2 = df[df["binyear"] == 2000]
        acc = df2[f"c{ctx['var']}"].cumsum()
        maxval = acc.max()
        ax.plot(
            range(1, len(acc.index) + 1),
            acc,
            label=f"NCEI91-20 - {maxval:.2f}",
            color="k",
            linestyle="--",
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
