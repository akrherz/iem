"""Climatologies comparison"""
import datetime
import calendar

from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot displays a comparison of various daily
    temperature climatologies.  The National Center for Environmental
    Information (NCEI) releases a 30 year climatology every ten years.  This
    data is smoothed to remove day to day variability.  The raw daily averages
    are shown computed from the daily observation archive maintained by the
    IEM."""
    desc["arguments"] = [
        # IATDSM has some troubles here
        dict(
            type="station",
            name="station",
            default="IA2203",
            network="IACLIMATE",
            label="Select Station:",
        ),
        dict(
            type="month",
            name="month",
            default=datetime.date.today().month,
            label="Select Month:",
        ),
        dict(
            type="year",
            min=1850,
            label="Minimum Inclusive Year (if data exists) for IEM Average",
            name="syear",
            default=1850,
        ),
        dict(
            type="year",
            min=1850,
            label="Maximum Inclusive Year (if data exists) for IEM Average",
            name="eyear",
            default=datetime.date.today().year,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]

    table = "alldata_%s" % (station[:2],)

    # beat month
    df = read_sql(
        f"""
    with obs as (
     SELECT sday, avg(high) as avgh, avg(low) as avgl,
     avg((high+low)/2.) as avgt, min(year) as min_year,
     max(year) as max_year from {table}
     WHERE station = %s and month = %s and year >= %s and year <= %s
     GROUP by sday
    ), c91 as (
     SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
     from ncei_climate91 where station = %s
    ), c81 as (
     SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
     from ncdc_climate81 where station = %s
    ), c71 as (
     SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
     from ncdc_climate71 where station = %s
    )

    SELECT o.sday, o.min_year, o.max_year,
    o.avgh as iem_avgh,
    c91.high as ncei91_avgh,
    c81.high as ncei81_avgh,
    c71.high as ncei71_avgh,
    o.avgl as iem_avgl,
    c91.low as ncei91_avgl,
    c81.low as ncei81_avgl,
    c71.low as ncei71_avgl,
    o.avgt as iem_avgt,
    c91.avgt as ncei91_avgt,
    c81.avgt as ncei81_avgt,
    c71.avgt as ncei71_avgt
    from obs o, c91, c81, c71 where o.sday = c81.sday and o.sday = c71.sday and
    o.sday = c91.sday ORDER by o.sday ASC
    """,
        pgconn,
        params=(
            station,
            month,
            ctx["syear"],
            ctx["eyear"],
            ctx["_nt"].sts[station]["ncei91"],
            ctx["_nt"].sts[station]["ncdc81"],
            station,
        ),
        index_col="sday",
    )
    if df.empty:
        raise NoDataFound("No Data Found.")

    (fig, ax) = plt.subplots(3, 1, sharex=True, figsize=(8, 6))

    ax[0].set_title(
        ("%s %s Daily Climate Comparison for %s")
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            calendar.month_name[month],
        ),
        fontsize=12,
    )
    x = list(range(1, len(df.index) + 1))
    for i, c in enumerate(["avgh", "avgl", "avgt"]):
        ax[i].bar(
            x,
            df[f"iem_{c}"],
            width=0.8,
            fc="tan",
            align="center",
            label="IEM %.0f-%.0f Obs Avg"
            % (
                df["min_year"].min(),
                df["max_year"].max(),
            ),
        )
        ax[i].plot(
            x,
            df[f"ncei91_{c}"],
            lw=2,
            zorder=2,
            color="b",
            label="NCEI 1991-2020",
        )
        ax[i].plot(
            x,
            df[f"ncei81_{c}"],
            lw=2,
            zorder=2,
            color="g",
            label="NCEI 1981-2010",
        )
        ax[i].plot(
            x,
            df[f"ncei71_{c}"],
            lw=2,
            zorder=2,
            color="r",
            label="NCEI 1971-2000",
        )
        ax[i].grid(True)
        ymin = (
            df[[f"iem_{c}", f"ncei91_{c}", f"ncei81_{c}", f"ncei71_{c}"]]
            .min()
            .min()
        )
        ax[i].set_ylim(bottom=ymin - 2)

    ax[0].set_ylabel(r"High Temp $^\circ$F")
    ax[1].set_ylabel(r"Low Temp $^\circ$F")
    ax[2].set_ylabel(r"Average Temp $^\circ$F")

    ax[2].legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1),
        fancybox=True,
        shadow=True,
        ncol=4,
        scatterpoints=1,
        fontsize=10,
    )

    ax[2].set_xlabel("Day of %s" % (calendar.month_name[month],))
    ax[2].set_xlim(0.5, len(x) + 0.5)

    ax[0].set_position([0.1, 0.7, 0.85, 0.24])
    ax[1].set_position([0.1, 0.42, 0.85, 0.24])
    ax[2].set_position([0.1, 0.1, 0.85, 0.24])

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="IA0200"))
