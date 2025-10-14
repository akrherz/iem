"""
This plot displays a comparison of various daily
temperature climatologies.  The National Center for Environmental
Information (NCEI) releases a 30 year climatology every ten years.  This
data is smoothed to remove day to day variability.  The raw daily averages
are shown computed from the daily observation archive maintained by the
IEM.
"""

import calendar
from datetime import date

import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure

from iemweb.autoplot import ARG_STATION


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="month",
            name="month",
            default=date.today().month,
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
            default=date.today().year,
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    month = ctx["month"]

    ncei91 = ctx["_nt"].sts[station]["ncei91"]
    ncei81 = ctx["_nt"].sts[station]["ncdc81"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        with obs as (
            SELECT sday, avg(high) as avgh, avg(low) as avgl,
            avg((high+low)/2.) as avgt, min(year) as min_year,
            max(year) as max_year from alldata
            WHERE station = :station and month = :month
            and year >= :syear and year <= :eyear
            GROUP by sday
        ), c91 as (
        SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
        from ncei_climate91 where station = :ncei91
        ), c81 as (
        SELECT to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
        from ncdc_climate81 where station = :ncei81
        ), c71 as (
        select to_char(valid, 'mmdd') as sday, high, low, (high+low)/2. as avgt
        from ncdc_climate71 where station = :climate_site
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
        from obs o LEFT JOIN c91 ON o.sday = c91.sday
        LEFT JOIN c81 ON o.sday = c81.sday
        LEFT JOIN c71 ON o.sday = c71.sday
        ORDER by o.sday ASC
        """),
            conn,
            params={
                "station": station,
                "month": month,
                "syear": ctx["syear"],
                "eyear": ctx["eyear"],
                "ncei91": ctx["_nt"].sts[station]["ncei91"],
                "ncei81": ctx["_nt"].sts[station]["ncdc81"],
                "climate_site": ctx["_nt"].sts[station]["climate_site"],
            },
            index_col="sday",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")

    title = (
        f"{ctx['_sname']} :: Daily "
        f"Climate Comparison for {calendar.month_name[month]}"
    )
    fig = figure(
        apctx=ctx,
        title=title,
        subtitle=(
            f"NCEI91 Station: {ncei91} NCEI81 Station: {ncei81} "
            f"NCEI71 Station: {ctx['_nt'].sts[station]['climate_site']}"
        ),
    )
    height = 0.21
    ax = [
        fig.add_axes((0.1, 0.08 + height * 2 + 0.18, 0.85, height)),
        fig.add_axes((0.1, 0.08 + height + 0.09, 0.85, height)),
        fig.add_axes((0.1, 0.08, 0.85, height)),
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
        for prefix, label, color in zip(
            ["ncei91", "ncei81", "ncei71"],
            ["NCEI 1991-2020", "NCEI 1981-2010", "NCEI 1971-2000"],
            ["red", "blue", "green"],
            strict=True,
        ):
            if df[f"{prefix}_{c}"].isna().all():
                continue
            ax[i].plot(
                x,
                df[f"{prefix}_{c}"],
                lw=2,
                zorder=2,
                color=color,
                label=label,
            )
        ax[i].grid(True)
        ymin = (
            df[[f"iem_{c}", f"ncei91_{c}", f"ncei81_{c}", f"ncei71_{c}"]]
            .min()
            .min()
        )
        ax[i].set_ylim(bottom=ymin - 2)

    ax[0].set_ylabel("High Temp °F")
    ax[1].set_ylabel("Low Temp °F")
    ax[2].set_ylabel("Average Temp °F")

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
