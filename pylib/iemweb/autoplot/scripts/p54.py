"""
This application plots the difference in morning
low or afternoon high temperature between two sites of your choice.
The morning is
defined as the period between midnight and 8 AM local time.  The afternoon
high is defined as the period between noon and 8 PM.  If any difference
is greater than 25 degrees, it is omitted from this analysis.  This app
may take a while to generate a plot, so please be patient!</p>

<p><a href="/plotting/auto/?q=250">Autoplot 250</a> generates a comparison
of an hourly variable between two sites.</p>
"""

import calendar
from datetime import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, get_cmap

PDICT = {
    "low": "Morning Low (midnight to 8 AM)",
    "high": "Afternoon High (noon to 8 PM)",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation1",
            default="ALO",
            network="IA_ASOS",
            label="Select Station 1:",
        ),
        dict(
            type="zstation",
            name="zstation2",
            default="OLZ",
            network="IA_ASOS",
            label="Select Station 2:",
        ),
        dict(
            type="select",
            name="varname",
            default="low",
            options=PDICT,
            label="Select Comparison",
        ),
        dict(type="cmap", name="cmap", default="Greens", label="Color Ramp:"),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station1 = ctx["zstation1"]
    station2 = ctx["zstation2"]
    varname = ctx["varname"]

    aggfunc = "min"
    tlimit = "0 and 8"
    if varname == "high":
        aggfunc = "max"
        tlimit = "12 and 20"
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper(
                """
        WITH one as (
        SELECT date(valid), {aggfunc}(tmpf::int) as d, avg(sknt)
        from alldata where station = :station1
        and extract(hour from valid at time zone :tz1) between {tlimit}
        and tmpf between -70 and 140  GROUP by date),

        two as (
        SELECT date(valid), {aggfunc}(tmpf::int) as d, avg(sknt)
        from alldata where station = :station2
        and extract(hour from valid at time zone :tz2) between {tlimit}
        and tmpf between -70 and 140 GROUP by date)

        SELECT one.date as day,
        extract(week from one.date) as week,
        one.d - two.d as delta,
        one.avg as sknt,
        two.avg as sknt2
        from one JOIN two on (one.date = two.date) WHERE one.avg >= 0
        and one.d - two.d between -25 and 25
        """,
                aggfunc=aggfunc,
                tlimit=tlimit,
            ),
            conn,
            params={
                "station1": station1,
                "tz1": ctx["_nt1"].sts[station1]["tzname"],
                "station2": station2,
                "tz2": ctx["_nt2"].sts[station2]["tzname"],
            },
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    sts = datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    fig = figure(apctx=ctx)
    ax = fig.subplots(2, 1)

    tt = "Mid - 8 AM Low" if varname == "low" else "Noon - 8 PM High"
    ax[0].set_title(
        f"[{station1}] {ctx['_nt1'].sts[station1]['name']} minus "
        f"[{station2}] {ctx['_nt2'].sts[station2]['name']}\n"
        f"{tt} Temp Difference Period: {df['day'].min()} - {df['day'].max()}"
    )

    bins = np.arange(-20.5, 20.5, 1)
    H, xedges, yedges = np.histogram2d(
        df["week"].to_numpy(),
        df["delta"].to_numpy(),
        [list(range(54)), list(bins)],
    )
    H = np.ma.array(H)
    H.mask = np.ma.where(H < 1, True, False)
    ax[0].pcolormesh(
        (xedges - 1) * 7, yedges, H.transpose(), cmap=get_cmap(ctx["cmap"])
    )
    ax[0].set_xticks(xticks)
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].set_xlim(0, 366)

    y = []
    for i in range(np.shape(H)[0]):
        y.append(np.ma.sum(H[i, :] * (bins[:-1] + 0.5)) / np.ma.sum(H[i, :]))  # noqa

    ax[0].plot(xedges[:-1] * 7, y, zorder=3, lw=3, color="k")
    ax[0].plot(xedges[:-1] * 7, y, zorder=3, lw=1, color="w")

    rng = min([max([df["delta"].max(), 0 - df["delta"].min()]), 12])
    ax[0].set_ylim(0 - rng - 2, rng + 2)
    ax[0].grid(True)
    ax[0].set_ylabel(
        f"{'Low' if varname == 'low' else 'High'} Temp Diff " r"$^\circ$F"
    )
    ax[0].text(
        -0.01,
        1.02,
        f"{station1}\nWarmer",
        transform=ax[0].transAxes,
        va="top",
        ha="right",
        fontsize=8,
    )
    ax[0].text(
        -0.01,
        -0.02,
        f"{station1}\nColder",
        transform=ax[0].transAxes,
        va="bottom",
        ha="right",
        fontsize=8,
    )

    H, xedges, yedges = np.histogram2d(
        df["sknt"].to_numpy(),
        df["delta"].to_numpy(),
        [list(range(31)), list(bins)],
    )
    H = np.ma.array(H)
    H.mask = np.where(H < 1, True, False)
    ax[1].pcolormesh(
        (xedges - 0.5), yedges, H.transpose(), cmap=get_cmap(ctx["cmap"])
    )

    y = []
    x = []
    for i in range(np.shape(H)[0]):
        _ = np.ma.sum(H[i, :] * (bins[:-1] + 0.5)) / np.ma.sum(H[i, :])
        if not np.ma.is_masked(_):
            x.append(xedges[i])
            y.append(_)

    ax[1].plot(x, y, zorder=3, lw=3, color="k")
    ax[1].plot(x, y, zorder=3, lw=1, color="w")

    ax[1].set_ylim(0 - rng - 2, rng + 2)
    ax[1].grid(True)
    ax[1].set_xlim(left=-0.25)
    ax[1].set_xlabel(f"Average Wind Speed [kts] for {station1}")
    ax[1].set_ylabel(
        f"{'Low' if varname == 'low' else 'High'} Temp Diff " r"$^\circ$F"
    )
    ax[1].text(
        -0.01,
        1.02,
        f"{station1}\nWarmer",
        transform=ax[1].transAxes,
        va="top",
        ha="right",
        fontsize=8,
    )
    ax[1].text(
        -0.01,
        -0.02,
        f"{station1}\nColder",
        transform=ax[1].transAxes,
        va="bottom",
        ha="right",
        fontsize=8,
    )

    return fig, df
