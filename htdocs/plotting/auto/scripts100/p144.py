"""ISUAG"""

from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable  # This is needed.
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn, utc, convert_value
from pyiem.exceptions import NoDataFound

XREF = {
    "AEEI4": "A130209",
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
    desc = dict()
    desc[
        "description"
    ] = """This plot uses hourly 4 inch depth soil
    temperature observations from the ISU Soil Moisture Network.  It first
    plots the first period each year that the soil temperature was at or
    above 50 degrees for at least X number of hours.  It then plots any
    subsequent periods below 50 degrees for that year."""
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="ISUSM",
            default="BOOI4",
            label="Select Station:",
        ),
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
    pgconn = get_dbconn("isuag")
    ctx = get_autoplot_context(fdict, get_description())
    threshold = 50
    threshold_c = convert_value(threshold, "degF", "degC")
    hours1 = ctx["hours1"]
    hours2 = ctx["hours2"]
    station = ctx["station"]
    oldstation = XREF[station]

    df = read_sql(
        """
    with obs as (
        select valid, c300, lag(c300) OVER (ORDER by valid ASC) from hourly
        where station = %s),
    agg1 as (
        select valid,
        case when c300 > %s and lag < %s then 1
             when c300 < %s and lag > %s then -1
             else 0 end as t from obs),
    agg2 as (
        SELECT valid, t from agg1 where t != 0),
    agg3 as (
        select valid, lead(valid) OVER (ORDER by valid ASC),
        t from agg2),
    agg4 as (
        select extract(year from valid) as yr, valid, lead,
        rank() OVER (PARTITION by extract(year from valid) ORDER by valid ASC)
        from agg3 where t = 1
        and (lead - valid) >= '%s hours'::interval),
    agg5 as (
        select extract(year from valid) as yr, valid, lead
        from agg3 where t = -1)

    select f.yr, f.valid as fup, f.lead as flead, d.valid as dup,
    d.lead as dlead from agg4 f JOIN agg5 d ON (f.yr = d.yr)
    where f.rank = 1 and d.valid > f.valid
    ORDER by fup ASC
    """,
        pgconn,
        params=(
            oldstation,
            threshold,
            threshold,
            threshold,
            threshold,
            hours1,
        ),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found")

    df2 = read_sql(
        """
    with obs as (
        select valid, t04_c_avg,
        lag(t04_c_avg) OVER (ORDER by valid ASC) from sm_hourly
        where station = %s),
    agg1 as (
        select valid,
        case when t04_c_avg > %s and lag < %s then 1
             when t04_c_avg < %s and lag > %s then -1
             else 0 end as t from obs),
    agg2 as (
        SELECT valid, t from agg1 where t != 0),
    agg3 as (
        select valid, lead(valid) OVER (ORDER by valid ASC),
        t from agg2),
    agg4 as (
        select extract(year from valid) as yr, valid, lead,
        rank() OVER (PARTITION by extract(year from valid) ORDER by valid ASC)
        from agg3 where t = 1
        and (lead - valid) >= '%s hours'::interval),
    agg5 as (
        select extract(year from valid) as yr, valid, lead
        from agg3 where t = -1)

    select f.yr, f.valid as fup, f.lead as flead, d.valid as dup,
    d.lead as dlead from agg4 f JOIN agg5 d ON (f.yr = d.yr)
    where f.rank = 1 and d.valid > f.valid
    ORDER by fup ASC
    """,
        pgconn,
        params=(
            station,
            threshold_c,
            threshold_c,
            threshold_c,
            threshold_c,
            hours1,
        ),
        index_col=None,
    )
    if df2.empty:
        raise NoDataFound("No Data Found")

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

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

    nt = NetworkTable("ISUSM")
    nt2 = NetworkTable("ISUAG", only_online=False)
    ab = nt.sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax.set_title(
        ("[%s] %s 4 Inch Soil Temps\n[%s] %s used for pre-%s dates")
        % (
            station,
            nt.sts[station]["name"],
            oldstation,
            nt2.sts[oldstation]["name"],
            ab.year,
        )
    )
    ax.set_ylim(df["yr"].min() - 1, df2["yr"].max() + 1)

    p0 = plt.Rectangle((0, 0), 1, 1, fc="r")
    p1 = plt.Rectangle((0, 0), 1, 1, fc="lightblue")
    p2 = plt.Rectangle((0, 0), 1, 1, fc="b")
    ax.legend(
        (p0, p1, p2),
        (
            "First Period Above %s for %s+ Hours" % (threshold, hours1),
            "Below %s for 1+ Hours" % (threshold,),
            "Below %s for %s+ Hours" % (threshold, hours2),
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


if __name__ == "__main__":
    plotter(dict())
