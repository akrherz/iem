"""
This application generates per WFO or state maps of VTEC
event counts.  The current three available metrics are:<br />
<ul>
    <li><strong>Event Count</strong>: The number of distinct VTEC events.
    A distinct event is simply the usage of one VTEC event identifier.</li>
    <li><strong>Days with 1+ Events</strong>: This is the number of days
    within the period of interest that had at least one VTEC event. A day
    is defined within the US Central Time Zone.  If one event crosses
    midnight, this would count as two days.</li>
    <li><strong>Percent of Time</strong>: This is the temporal coverage
    percentage within the period of interest.  Rewording, what percentage
    of the time was at least one event active.</li>
    <li><strong>Rank of Event Count</strong>: The ranking from least to
    greatest of the given period's event count vs period of record
    climatology.</li>
    <li><strong>Departure from Average of Event Count</strong>: The number
    of events that the given period differs from the period of record
    climatology.</li>
    <li>
    <strong>Standardized Departure from Average of Event Count</strong>:
    The departure expressed in sigma units of this periods event total
    vs the period of record climatology.</li>
</ul></p>

<p><strong>PLEASE USE CAUTION</strong> with the departure from average
plots as they are not exactly straight forward to compute.  If you are
plotting small periods of time, individual events will heavily skew the
averages.  The exact start date of each event type is not an exact
science due to the implementation of some products and other complexities.
For Severe Thunderstorm, Tornado, Flash Flood, and Marine Warnings, the
IEM has a special accounting of these back to 2002.  For other event
types, the archive starts with the VTEC implementation, which varies by
product.</p>

<p>Note that various VTEC events have differenting start periods of record.
Most products go back to October 2005.</p>
"""

from datetime import date, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import MapPlot, get_cmap

PDICT = {
    "count": "Event Count",
    "days": "Days with 1+ Events",
    "tpercent": "Percent of Time",
    "count_rank": "Rank of Event Count (1=lowest)",
    "count_departure": "Departure from Average of Event Count",
    "count_standard": "Standardized Departure from Average of Event Count",
}
PDICT2 = {
    "all": "Use All VTEC Events",
    "set": "Use Requested VTEC Events From Form",
}
PDICT3 = {
    "pds": "Only PDS",
    "yes": "Only Emergencies",
    "all": "All Events",
}
PDICT4 = {
    "wfo": "by WFO",
    "state": "by State",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    desc["data"] = True
    today = date.today()
    jan1 = today.replace(month=1, day=1)
    tomorrow = today + timedelta(days=1)
    desc["arguments"] = [
        dict(
            type="select",
            name="by",
            options=PDICT4,
            default="wfo",
            label="Aggregate Statistics:",
        ),
        dict(
            type="datetime",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d 0000"),
            label="Start Date / Time (UTC, inclusive):",
            min="2002/01/01 0000",
        ),
        dict(
            type="datetime",
            name="edate",
            default=today.strftime("%Y/%m/%d 2359"),
            label="End Date / Time (UTC):",
            min="2002/01/01 0000",
            max=f"{tomorrow:%Y/%m/%d} 2359",
        ),
        dict(
            type="select",
            name="var",
            default="count",
            options=PDICT,
            label="Which metric to plot:",
        ),
        dict(
            type="select",
            name="w",
            default="set",
            options=PDICT2,
            label="Option to plot all or form set VTEC Events:",
        ),
        dict(
            type="vtec_ps",
            name="v1",
            default="SV.W",
            label="VTEC Phenomena and Significance 1",
        ),
        dict(
            type="vtec_ps",
            name="v2",
            default="SV.W",
            optional=True,
            label="VTEC Phenomena and Significance 2",
        ),
        dict(
            type="vtec_ps",
            name="v3",
            default="SV.W",
            optional=True,
            label="VTEC Phenomena and Significance 3",
        ),
        dict(
            type="vtec_ps",
            name="v4",
            default="SV.W",
            optional=True,
            label="VTEC Phenomena and Significance 4",
        ),
        dict(
            type="select",
            name="e",
            default="all",
            label="Only plot Emergencies / PDS ?",
            options=PDICT3,
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def get_count_df(ctx, varname: str, pstr, sts, ets):
    """Oh boy, do complex things."""

    emerg_extra = ""
    if ctx["e"] == "yes":
        emerg_extra = " and is_emergency "
    elif ctx["e"] == "pds":
        emerg_extra = " and is_pds "
    params = {}
    if varname.startswith("count_"):
        if (ets - sts).days > 366:
            raise NoDataFound("Can't compute over period > 366 days")
        params["sday"] = f"{sts:%m%d}"
        params["eday"] = f"{ets:%m%d}"
        slimiter = (
            " (to_char(issue, 'mmdd') >= :sday and "
            "to_char(issue, 'mmdd') <= :eday ) "
        )
        yearcol = "vtec_year"
        if ets <= sts:
            slimiter = slimiter.replace(" and ", " or ")
            yearcol = (
                "case when to_char(issue, 'mmdd') <= :eday then "
                "vtec_year - 1 else vtec_year end"
            )

        # compute all the things.
        params["sdate"] = "2002-01-01"
        if pstr.find("1=1") > -1:
            params["sdate"] = "2005-10-01"
        with get_sqlalchemy_conn("postgis") as conn:
            if ctx["by"] == "state":
                sql = """
                with events as (
                    select distinct wfo, substr(ugc, 1, 2) as state,
                    {yearcol} as year,
                    phenomena, eventid from warnings where {pstr} and
                    {slimiter} and issue > :sdate {emerg_extra})
                select state as datum, year::int as year, count(*) from events
                group by datum, year
                """
            else:
                sql = """
                with events as (
                    select distinct wfo, {yearcol} as year,
                    phenomena, eventid from warnings where {pstr} and
                    {slimiter} and issue > :sdate {emerg_extra})
                select wfo as datum, year::int as year, count(*) from events
                group by datum, year
                """
            df = pd.read_sql(
                sql_helper(
                    sql,
                    yearcol=yearcol,
                    slimiter=slimiter,
                    pstr=pstr,
                    emerg_extra=emerg_extra,
                ),
                conn,
                params=params,
                index_col=None,
            )
        # enlarge by wfo and year cartesian product
        ctx["_subtitle"] = (
            ", Period of Record: "
            f"{df['year'].min():.0f}-{df['year'].max():.0f}"
        )
        idx = pd.MultiIndex.from_product(
            [df["datum"].unique(), df["year"].unique()],
            names=["datum", "year"],
        )
        df = (
            df.set_index(["datum", "year"])
            .reindex(idx)
            .fillna(0)
            .reset_index()
        )
        df["rank"] = df.groupby("datum")["count"].rank(
            method="min", ascending=True
        )
        thisyear = (
            df[df["year"] == sts.year].set_index("datum").drop("year", axis=1)
        )
        # Ready to construct final df.
        df = (
            df[["datum", "count"]].groupby("datum").agg(["mean", "std"]).copy()
        )
        df.columns = ["_".join(a) for a in df.columns.to_flat_index()]
        df[["count", "count_rank"]] = thisyear[["count", "rank"]]
        df["count_departure"] = df["count"] - df["count_mean"]
        df["count_standard"] = df["count_departure"] / df["count_std"]
    else:
        with get_sqlalchemy_conn("postgis") as conn:
            if ctx["by"] == "state":
                sql = """
                with total as (
                select distinct wfo, substr(ugc, 1, 2) as state,
                extract(year from issue at time zone 'UTC') as year,
                phenomena, significance, eventid from warnings
                where {pstr} and issue >=:sts and issue < :ets {emerg_extra}
                )

                SELECT state as datum, count(*) from total
                GROUP by datum
                """
            else:
                sql = """
                with total as (
                select distinct wfo,
                extract(year from issue at time zone 'UTC') as year,
                phenomena, significance, eventid from warnings
                where {pstr} and issue >= :sts and issue < :ets {emerg_extra}
                )

                SELECT wfo as datum, count(*) from total
                GROUP by datum
                """
            df = pd.read_sql(
                sql_helper(sql, pstr=pstr, emerg_extra=emerg_extra),
                conn,
                params={"sts": sts, "ets": ets},
                index_col="datum",
            )
    return df


def get_count_bins(df, varname):
    """Figure out sensible bins."""
    minv = df[varname].min()
    maxv = df[varname].max()
    if pd.isna(maxv):
        return np.arange(1, 10, 1)
    if varname == "count_rank":
        bins = np.arange(1, maxv + 2)
    elif varname == "count":
        bins = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 200]
        if maxv > 5000:
            bins = [
                1,
                5,
                10,
                50,
                100,
                250,
                500,
                750,
                1000,
                1500,
                2000,
                3000,
                5000,
                7500,
                10000,
            ]
        elif maxv > 1000:
            bins = [
                1,
                5,
                10,
                50,
                100,
                150,
                200,
                250,
                500,
                750,
                1000,
                1250,
                1500,
                2000,
            ]
        elif maxv > 200:
            bins = [
                1,
                3,
                5,
                10,
                20,
                35,
                50,
                75,
                100,
                150,
                200,
                250,
                500,
                750,
                1000,
            ]
        elif maxv < 75:
            bins = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75]
    elif max([abs(minv), abs(maxv)]) > 100:
        bins = [-200, -150, -100, -50, -25, -10, 0, 10, 25, 50, 100, 150, 200]
    elif max([abs(minv), abs(maxv)]) > 10:
        bins = [-100, -50, -25, -10, -5, 0, 5, 10, 25, 50, 100]
    else:
        bins = np.arange(-3, 3.1, 0.5)
    return bins


def plotter(ctx: dict):
    """Go"""
    sts = ctx["sdate"].replace(tzinfo=ZoneInfo("UTC"))
    ets = ctx["edate"].replace(tzinfo=ZoneInfo("UTC"))
    p1 = ctx["phenomenav1"]
    p2 = ctx["phenomenav2"]
    p3 = ctx["phenomenav3"]
    p4 = ctx["phenomenav4"]
    varname = ctx["var"]
    phenomena = [p[:2] for p in [p1, p2, p3, p4] if p is not None]
    s1 = ctx["significancev1"]
    s2 = ctx["significancev2"]
    s3 = ctx["significancev3"]
    s4 = ctx["significancev4"]
    significance = [s[0] for s in [s1, s2, s3, s4] if s is not None]

    pstr = []
    subtitle = ""
    title = ""
    for p, s in zip(phenomena, significance):
        pstr.append(f"(phenomena = '{p}' and significance = '{s}')")
        subtitle += f"{p}.{s} "
        title += vtec.get_ps_string(p, s)
    if len(phenomena) > 1:
        title = "VTEC Unique Event"
    pstr = " or ".join(pstr)
    pstr = f"({pstr})"
    if ctx["w"] == "all":
        pstr = " 1=1 "
        subtitle = "All"
        title = "All VTEC Events"
    cmap = get_cmap(ctx["cmap"])

    extend = "neither"
    emerg_extra = ""
    if ctx["e"] == "yes":
        emerg_extra = " and is_emergency "
        title += " (Emergencies) "
    elif ctx["e"] == "pds":
        emerg_extra = " and is_pds "
        title += " (Particularly Dangerous Situation) "
    subtitle_extra = ""
    if varname.startswith("count"):
        df = get_count_df(ctx, varname, pstr, sts, ets)

        bins = get_count_bins(df, varname)
        lformat = "%.0f"
        units = "Count"
        if varname == "count":
            extend = "max"
            # Can't do state as events are double counted
            if ctx["by"] == "wfo":
                subtitle_extra = (
                    f" {df['count'].sum():,.0f} Events over "
                    f"{len(df.index):.0f} WFOs"
                )
        elif varname == "count_rank":
            extend = "neither"
            units = "Rank"
        else:
            if varname == "count_standard":
                lformat = "%.1f"
                units = "sigma"
            extend = "both"
        df2 = df[varname]
    elif varname == "days":
        with get_sqlalchemy_conn("postgis") as conn:
            if ctx["by"] == "state":
                sql = """
            WITH data as (
                SELECT distinct substr(ugc, 1, 2) as state,
                generate_series(greatest(issue, :sts),
                least(expire, :ets), '1 minute'::interval) as ts from warnings
                WHERE issue > :sts and expire < :ets and {pstr} {emerg_extra}
            ), agg as (
                SELECT distinct state, date(ts) from data
            )
            select state as datum, count(*) as days from agg
            GROUP by datum ORDER by days DESC
            """
            else:
                sql = """
            WITH data as (
                SELECT distinct wfo, generate_series(greatest(issue, :sts),
                least(expire, :ets), '1 minute'::interval) as ts from warnings
                WHERE issue > :sts2 and expire < :ets2 and {pstr} {emerg_extra}
            ), agg as (
                SELECT distinct wfo, date(ts) from data
            )
            select wfo as datum, count(*) as days from agg
            GROUP by datum ORDER by days DESC
            """
            df = pd.read_sql(
                sql_helper(sql, pstr=pstr, emerg_extra=emerg_extra),
                conn,
                params={
                    "sts": sts,
                    "ets": ets,
                    "sts2": sts - timedelta(days=90),
                    "ets2": ets + timedelta(days=90),
                },
                index_col="datum",
            )

        df2 = df["days"]
        if df2.max() < 10:
            bins = list(range(1, 11, 1))
        else:
            bins = np.linspace(1, df["days"].max() + 11, 10, dtype="i")
        units = "Days"
        lformat = "%.0f"
        cmap.set_under("white")
        cmap.set_over("#EEEEEE")
    else:
        total_minutes = (ets - sts).total_seconds() / 60.0
        with get_sqlalchemy_conn("postgis") as conn:
            if ctx["by"] == "state":
                sql = """
            WITH data as (
                SELECT distinct substr(ugc, 1, 2) as state,
                generate_series(greatest(issue, :sts),
                least(expire, :ets), '1 minute'::interval) as ts from warnings
                WHERE issue > :sts2 and expire < :ets2 and {pstr} {emerg_extra}
            )
            select state as datum,
            count(*) / cast(:mins as real) * 100. as tpercent
            from data GROUP by datum ORDER by tpercent DESC
            """
            else:
                sql = """
            WITH data as (
                SELECT distinct wfo, generate_series(greatest(issue, :sts),
                least(expire, :ets), '1 minute'::interval) as ts from warnings
                WHERE issue > :sts2 and expire < :ets2 and {pstr} {emerg_extra}
            )
            select wfo as datum,
            count(*) / cast(:mins as real) * 100. as tpercent
            from data GROUP by datum ORDER by tpercent DESC
            """
            df = pd.read_sql(
                sql_helper(sql, pstr=pstr, emerg_extra=emerg_extra),
                conn,
                params={
                    "sts": sts,
                    "ets": ets,
                    "sts2": sts - timedelta(days=90),
                    "ets2": ets + timedelta(days=90),
                    "mins": total_minutes,
                },
                index_col="datum",
            )

        df2 = df["tpercent"]
        bins = list(range(0, 101, 10))
        if df2.max() < 5:
            bins = np.arange(0, 5.1, 0.5)
        elif df2.max() < 10:
            bins = list(range(0, 11, 1))
        units = "Percent"
        lformat = "%.1f"

    mp = MapPlot(
        apctx=ctx,
        sector="nws",
        axisbg="white",
        nocaption=True,
        title=f"{title} {PDICT[varname]} {PDICT4[ctx['by']]}",
        subtitle=(
            f"Issued between {sts:%d %b %Y %H:%M} - {ets:%d %b %Y %H:%M} UTC, "
            f"based on VTEC: {subtitle} {ctx.get('_subtitle', '')}"
            f"{subtitle_extra}"
        ),
    )
    func = mp.fill_cwas if ctx["by"] == "wfo" else mp.fill_states
    if df2.empty:
        mp.fig.text(
            0.5,
            0.5,
            "No Events Found",
            ha="center",
            va="center",
            fontsize="large",
        )
    else:
        func(
            df2,
            bins=bins,
            ilabel=True,
            units=units,
            lblformat=lformat,
            cmap=cmap,
            extend=extend,
            labelbuffer=0,
        )

    return mp.fig, df
