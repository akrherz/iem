"""
This plot displays a comparison of various daily
temperature climatologies.  The National Center for Environmental
Information (NCEI) releases a 30 year climatology every ten years.  This
data is smoothed to remove day to day variability.  The raw daily averages
are shown computed from the daily observation archive maintained by the
IEM.
"""
import calendar
import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        # IATDSM has some troubles here
        dict(
            type="station",
            name="station",
            default="IATDSM",
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
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    month = ctx["month"]

    # beat month
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        with obs as (
        SELECT sday, avg(high) as avgh, avg(low) as avgl,
        avg((high+low)/2.) as avgt, min(year) as min_year,
        max(year) as max_year from alldata
        WHERE station = %s and month = %s and year >= %s and year <= %s
        GROUP by sday
        ), c91 as (
        SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
        from ncei_climate91 where station = %s
        ), c81 as (
        SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
        from ncdc_climate81 where station = %s
        )

        SELECT o.sday, o.min_year, o.max_year,
        o.avgh as iem_avgh,
        c91.high as ncei91_avgh,
        c81.high as ncei81_avgh,
        o.avgl as iem_avgl,
        c91.low as ncei91_avgl,
        c81.low as ncei81_avgl,
        o.avgt as iem_avgt,
        c91.avgt as ncei91_avgt,
        c81.avgt as ncei81_avgt
        from obs o, c91, c81 where o.sday = c81.sday
        and o.sday = c91.sday ORDER by o.sday ASC
        """,
            conn,
            params=(
                station,
                month,
                ctx["syear"],
                ctx["eyear"],
                ctx["_nt"].sts[station]["ncei91"],
                ctx["_nt"].sts[station]["ncdc81"],
            ),
            index_col="sday",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    title = (
        f"{ctx['_sname']} :: Daily "
        f"Climate Comparison for {calendar.month_name[month]}"
    )
    fig = figure(apctx=ctx, title=title)
    height = 0.21
    ax = [
        fig.add_axes([0.1, 0.08 + height * 2 + 0.18, 0.85, height]),
        fig.add_axes([0.1, 0.08 + height + 0.09, 0.85, height]),
        fig.add_axes([0.1, 0.08, 0.85, height]),
    ]
    x = list(range(1, len(df.index) + 1))
    for i, c in enumerate(["avgh", "avgl", "avgt"]):
        ax[i].bar(
            x,
            df[f"iem_{c}"],
            width=0.8,
            fc="tan",
            align="center",
            label=(
                f"IEM {df['min_year'].min():.0f}-{df['max_year'].max():.0f} "
                "Obs Avg"
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
        ax[i].grid(True)
        ymin = df[[f"iem_{c}", f"ncei91_{c}", f"ncei81_{c}"]].min().min()
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

    ax[2].set_xlabel(f"Day of {calendar.month_name[month]}")
    ax[2].set_xlim(0.5, len(x) + 0.5)

    return fig, df


if __name__ == "__main__":
    plotter({})
