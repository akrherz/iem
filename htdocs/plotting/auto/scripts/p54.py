"""ASOS comparisons"""
import datetime
import calendar

import numpy as np
from pandas.io.sql import read_sql
from pyiem.plot import get_cmap
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {
    "low": "Morning Low (midnight to 8 AM)",
    "high": "Afternoon High (noon to 8 PM)",
}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This application plots the difference in morning
    low or afternoon high temperature between two sites of your choice.
    The morning is
    defined as the period between midnight and 8 AM local time.  The afternoon
    high is defined as the period between noon and 8 PM.  If any difference
    is greater than 25 degrees, it is omitted from this analysis.  This app
    may take a while to generate a plot, so please be patient!"""
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
            network="AWOS",
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


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())
    station1 = ctx["zstation1"]
    station2 = ctx["zstation2"]
    varname = ctx["varname"]

    aggfunc = "min"
    tlimit = "0 and 8"
    if varname == "high":
        aggfunc = "max"
        tlimit = "12 and 20"
    df = read_sql(
        """
    WITH one as (
      SELECT date(valid), """
        + aggfunc
        + """(tmpf::int) as d, avg(sknt)
      from alldata where station = %s
      and extract(hour from valid at time zone %s) between """
        + tlimit
        + """
      and tmpf between -70 and 140  GROUP by date),

    two as (
      SELECT date(valid), """
        + aggfunc
        + """(tmpf::int) as d, avg(sknt)
      from alldata where station = %s
      and extract(hour from valid at time zone %s) between """
        + tlimit
        + """
      and tmpf between -70 and 140 GROUP by date)

    SELECT one.date as day,
    extract(week from one.date) as week,
    one.d - two.d as delta,
    one.avg as sknt,
    two.avg as sknt2
    from one JOIN two on (one.date = two.date) WHERE one.avg >= 0
    and one.d - two.d between -25 and 25
    """,
        pgconn,
        params=(
            station1,
            ctx["_nt1"].sts[station1]["tzname"],
            station2,
            ctx["_nt2"].sts[station2]["tzname"],
        ),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    (fig, ax) = plt.subplots(2, 1, figsize=(8, 6))

    ax[0].set_title(
        ("[%s] %s minus [%s] %s\n" "%s Temp Difference Period: %s - %s")
        % (
            station1,
            ctx["_nt1"].sts[station1]["name"],
            station2,
            ctx["_nt2"].sts[station2]["name"],
            "Mid - 8 AM Low" if varname == "low" else "Noon - 8 PM High",
            df["day"].min(),
            df["day"].max(),
        )
    )

    bins = np.arange(-20.5, 20.5, 1)
    H, xedges, yedges = np.histogram2d(
        df["week"].values, df["delta"].values, [range(0, 54), bins]
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
        y.append(np.ma.sum(H[i, :] * (bins[:-1] + 0.5)) / np.ma.sum(H[i, :]))

    ax[0].plot(xedges[:-1] * 7, y, zorder=3, lw=3, color="k")
    ax[0].plot(xedges[:-1] * 7, y, zorder=3, lw=1, color="w")

    rng = min([max([df["delta"].max(), 0 - df["delta"].min()]), 12])
    ax[0].set_ylim(0 - rng - 2, rng + 2)
    ax[0].grid(True)
    ax[0].set_ylabel(
        ("%s Temp Diff " r"$^\circ$F")
        % ("Low" if varname == "low" else "High",)
    )
    ax[0].text(
        -0.01,
        1.02,
        "%s\nWarmer" % (station1,),
        transform=ax[0].transAxes,
        va="top",
        ha="right",
        fontsize=8,
    )
    ax[0].text(
        -0.01,
        -0.02,
        "%s\nColder" % (station1,),
        transform=ax[0].transAxes,
        va="bottom",
        ha="right",
        fontsize=8,
    )

    H, xedges, yedges = np.histogram2d(
        df["sknt"].values, df["delta"].values, [range(0, 31), bins]
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
    ax[1].set_xlabel("Average Wind Speed [kts] for %s" % (station1,))
    ax[1].set_ylabel(
        ("%s Temp Diff " r"$^\circ$F")
        % ("Low" if varname == "low" else "High",)
    )
    ax[1].text(
        -0.01,
        1.02,
        "%s\nWarmer" % (station1,),
        transform=ax[1].transAxes,
        va="top",
        ha="right",
        fontsize=8,
    )
    ax[1].text(
        -0.01,
        -0.02,
        "%s\nColder" % (station1,),
        transform=ax[1].transAxes,
        va="bottom",
        ha="right",
        fontsize=8,
    )

    return fig, df


if __name__ == "__main__":
    plotter(dict())
