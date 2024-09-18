"""
This plot uses hourly 4 inch depth soil
temperature observations from the ISU Soil Moisture Network.  It first
plots the first period each year that the soil temperature was at or
above a threshold degrees for at least X number of hours.  It then plots any
subsequent periods below 50 degrees for that year.
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable  # This is needed.
from pyiem.plot import figure_axes
from pyiem.plot.use_agg import plt
from pyiem.util import convert_value, get_autoplot_context, utc
from sqlalchemy import text

XREF = {
    "AEEI4": "A130209",
    "AHDI4": "A130209",
    "BOOI4": "A130209",
    "CAMI4": "A138019",
    "CHAI4": "A131559",
    "CIRI4": "A131329",
    "CNAI4": "A131299",
    "CRFI4": "A131909",
    "DONI4": "A138019",
    "FRUI4": "A135849",
    "GREI4": "A134759",
    "KNAI4": "A134309",
    "NASI4": "A135879",
    "NWLI4": "A138019",
    "OKLI4": "A134759",
    "SBEI4": "A138019",
    "WMNI4": "A135849",
    "WTPI4": "A135849",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="ISUSM",
            default="BOOI4",
            label="Select Station:",
        ),
        {
            "type": "int",
            "name": "threshold",
            "default": 50,
            "label": "Threshold Temperature (F)",
        },
        dict(
            type="int",
            name="hours1",
            default=48,
            label="Stretch of Hours Above Threshold",
        ),
        dict(
            type="int",
            name="hours2",
            default=24,
            label="Stretch of Hours Below Threshold",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    threshold = ctx["threshold"]
    threshold_c = convert_value(threshold, "degF", "degC")
    hours1 = ctx["hours1"]
    hours2 = ctx["hours2"]
    station = ctx["station"]
    oldstation = XREF.get(station, "A130209")
    with get_sqlalchemy_conn("isuag") as conn:
        df2 = pd.read_sql(
            text("""
        with obs as (
            select valid, t4_c_avg_qc,
            lag(t4_c_avg_qc) OVER (ORDER by valid ASC) from sm_hourly
            where station = :station),
        agg1 as (
            select valid,
            case when t4_c_avg_qc > :t and lag < :t then 1
                when t4_c_avg_qc < :t and lag > :t then -1
                else 0 end as t from obs),
        agg2 as (
            SELECT valid, t from agg1 where t != 0),
        agg3 as (
            select valid, lead(valid) OVER (ORDER by valid ASC),
            t from agg2),
        agg4 as (
            select extract(year from valid) as yr, valid, lead,
            rank() OVER (PARTITION by extract(year from valid)
            ORDER by valid ASC)
            from agg3 where t = 1
            and (lead - valid) >= ':hrs hours'::interval),
        agg5 as (
            select extract(year from valid) as yr, valid, lead
            from agg3 where t = -1)

        select f.yr, f.valid as fup, f.lead as flead, d.valid as dup,
        d.lead as dlead from agg4 f JOIN agg5 d ON (f.yr = d.yr)
        where f.rank = 1 and d.valid > f.valid
        ORDER by fup ASC
        """),
            conn,
            params={
                "station": station,
                "t": threshold_c,
                "hrs": hours1,
            },
            index_col=None,
        )
        if df2.empty:
            raise NoDataFound("No Data Found")
        df = pd.read_sql(
            text("""
        with obs as (
            select valid, c300, lag(c300) OVER (ORDER by valid ASC) from hourly
            where station = :oldstation),
        agg1 as (
            select valid,
            case when c300 > :thres and lag < :thres then 1
                when c300 < :thres and lag > :thres then -1
                else 0 end as t from obs),
        agg2 as (
            SELECT valid, t from agg1 where t != 0),
        agg3 as (
            select valid, lead(valid) OVER (ORDER by valid ASC),
            t from agg2),
        agg4 as (
            select extract(year from valid) as yr, valid, lead,
            rank() OVER (PARTITION by extract(year from valid)
            ORDER by valid ASC)
            from agg3 where t = 1
            and (lead - valid) >= ':hours hours'::interval),
        agg5 as (
            select extract(year from valid) as yr, valid, lead
            from agg3 where t = -1)

        select f.yr, f.valid as fup, f.lead as flead, d.valid as dup,
        d.lead as dlead from agg4 f JOIN agg5 d ON (f.yr = d.yr)
        where f.rank = 1 and d.valid > f.valid
        ORDER by fup ASC
        """),
            conn,
            params={
                "oldstation": oldstation,
                "thres": threshold,
                "hours": hours1,
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found for legacy station")

    nt = NetworkTable("ISUSM")
    nt2 = NetworkTable("ISUAG", only_online=False)
    ab = nt.sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = (
        f"[{station}] {nt.sts[station]['name']} 4 Inch Soil Temps\n"
        f"[{oldstation}] {nt2.sts[oldstation]['name']} used for pre-{ab.year} "
        "dates"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)

    d2000 = utc(2000, 1, 1, 6)
    for d in [df, df2]:
        for _, row in d.iterrows():
            if row["dlead"] is None:
                continue
            f0 = (row["fup"].replace(year=2000) - d2000).total_seconds()
            f1 = (row["flead"].replace(year=2000) - d2000).total_seconds()
            d0 = (row["dup"].replace(year=2000) - d2000).total_seconds()
            d1 = (row["dlead"].replace(year=2000) - d2000).total_seconds()
            if d1 < d0:
                continue
            ax.barh(
                row["fup"].year,
                (f1 - f0),
                left=f0,
                facecolor="r",
                align="center",
                edgecolor="r",
            )
            color = "lightblue" if (d1 - d0) < (hours2 * 3600) else "b"
            ax.barh(
                row["fup"].year,
                (d1 - d0),
                left=d0,
                facecolor=color,
                align="center",
                edgecolor=color,
            )

    xticks = []
    xticklabels = []
    for i in range(1, 13):
        d2 = d2000.replace(month=i)
        xticks.append((d2 - d2000).total_seconds())
        xticklabels.append(d2.strftime("%-d %b"))
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(xticks[2], xticks[6])
    ax.grid(True)

    ax.set_ylim(df["yr"].min() - 1, df2["yr"].max() + 1)

    p0 = plt.Rectangle((0, 0), 1, 1, fc="r")
    p1 = plt.Rectangle((0, 0), 1, 1, fc="lightblue")
    p2 = plt.Rectangle((0, 0), 1, 1, fc="b")
    ax.legend(
        (p0, p1, p2),
        (
            f"First Period Above {threshold} for {hours1}+ Hours",
            f"Below {threshold} for 1+ Hours",
            f"Below {threshold} for {hours2}+ Hours",
        ),
        ncol=2,
        fontsize=11,
        loc=(0.0, -0.2),
    )
    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
    )

    return fig, df
