"""Replicated 108 plot, but for non-climodat."""
import datetime
from collections import OrderedDict

from pandas.io.sql import read_sql
import pandas as pd
import numpy as np
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = OrderedDict(
    [
        ("all", "Show All Three Plots"),
        ("gdd", "Show just Growing Degree Days"),
        ("precip", "Show just Precipitation"),
        ("sdd", "Show just Stress Degree Days"),
    ]
)


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """
    This plot presents accumulated totals and departures
    of growing degree days, precipitation and stress degree days. Leap days
    are not considered for this plot. The light blue area represents the
    range of accumulated values based on the climatology for the site. The
    climatology is based on the closest nearby long-term climate site.
    """
    today = datetime.date.today()
    if today.month < 5:
        today = today.replace(year=today.year - 1, month=10, day=1)
    sts = today.replace(month=5, day=1)

    desc["arguments"] = [
        dict(
            type="sid",
            name="station",
            default="AEEI4",
            network="ISUSM",
            label="Select Station",
        ),
        dict(
            type="date",
            name="sdate",
            default=sts.strftime("%Y/%m/%d"),
            label="Start Date (inclusive):",
            min="1893/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date (inclusive):",
            min="1893/01/01",
        ),
        dict(
            type="int",
            name="base",
            default="50",
            label="Growing Degree Day Base (F)",
        ),
        dict(
            type="int",
            name="ceil",
            default="86",
            label="Growing Degree Day Ceiling (F)",
        ),
        dict(
            type="year",
            name="year2",
            default=1893,
            optional=True,
            label="Compare with year (optional):",
        ),
        dict(
            type="year",
            name="year3",
            default=1893,
            optional=True,
            label="Compare with year (optional)",
        ),
        dict(
            type="year",
            name="year4",
            default=1893,
            optional=True,
            label="Compare with year (optional)",
        ),
        dict(
            type="select",
            name="which",
            default="all",
            options=PDICT,
            label="Which Charts to Show in Plot",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("iem")
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    year2 = ctx.get("year2", 0)
    year3 = ctx.get("year3", 0)
    year4 = ctx.get("year4", 0)
    wantedyears = [sdate.year, year2, year3, year4]
    yearcolors = ["r", "g", "b", "purple"]
    gddbase = ctx["base"]
    gddceil = ctx["ceil"]
    whichplots = ctx["which"]
    glabel = "gdd%s%s" % (gddbase, gddceil)

    # Make sure we have climo info
    if (
        station not in ctx["_nt"].sts
        or ctx["_nt"].sts[station]["climate_site"] is None
    ):
        raise NoDataFound("Unknown station metadata.")

    # build the climatology
    climosite = ctx["_nt"].sts[station]["climate_site"]
    climo = read_sql(
        f"SELECT day, sday, gddxx(%s, %s, high, low) as {glabel}, "
        "sdd86(high, low) as sdd86, precip "
        f"from alldata_{climosite[:2]} WHERE station = %s and "
        "year >= 1951 ORDER by day ASC",
        get_dbconn("coop"),
        params=(gddbase, gddceil, ctx["_nt"].sts[station]["climate_site"]),
        index_col="day",
    )
    baseyear = int(climo.index.values[0].year)
    years = (datetime.datetime.now().year - baseyear) + 1
    xlen = int((edate - sdate).days) + 1  # In case of leap day
    acc = np.zeros((years, xlen))
    acc[:] = np.nan
    pacc = np.zeros((years, xlen))
    pacc[:] = np.nan
    sacc = np.zeros((years, xlen))
    sacc[:] = np.nan
    for year in range(baseyear, datetime.datetime.now().year + 1):
        sts = sdate.replace(year=year)
        ets = sts + datetime.timedelta(days=(xlen - 1))
        x = climo.loc[sts:ets, glabel].cumsum()
        if x.empty:
            continue
        acc[(year - baseyear), : len(x.index)] = x.values
        x = climo.loc[sts:ets, "precip"].cumsum()
        pacc[(year - baseyear), : len(x.index)] = x.values
        x = climo.loc[sts:ets, "sdd86"].cumsum()
        sacc[(year - baseyear), : len(x.index)] = x.values

    sday_climo = climo.groupby("sday").mean()
    rows = []
    for i in range(xlen):
        date = sdate + datetime.timedelta(days=i)
        sday = date.strftime("%m%d")
        rows.append(
            {
                "sday": sday,
                f"c{glabel}": sday_climo.at[sday, glabel],
                f"c{glabel}_acc": np.nanmean(acc[:, i]),
                f"c{glabel}_min_acc": np.nanmin(acc[:, i]),
                f"c{glabel}_max_acc": np.nanmax(acc[:, i]),
                "cprecip": sday_climo.at[sday, "precip"],
                "cprecip_acc": np.nanmean(pacc[:, i]),
                "cprecip_min_acc": np.nanmin(pacc[:, i]),
                "cprecip_max_acc": np.nanmax(pacc[:, i]),
                "csdd86": sday_climo.at[sday, "sdd86"],
                "csdd86_acc": np.nanmean(sacc[:, i]),
                "csdd86_min_acc": np.nanmin(sacc[:, i]),
                "csdd86_max_acc": np.nanmax(sacc[:, i]),
            }
        )
    climo = pd.DataFrame(rows)

    # build the obs
    df = read_sql(
        "SELECT day, to_char(day, 'mmdd') as sday, "
        f"gddxx(%s, %s, max_tmpf, min_tmpf) as o{glabel}, pday as oprecip, "
        "sdd86(max_tmpf, min_tmpf) as osdd86 from summary s JOIN stations t "
        "ON (s.iemid = t.iemid) "
        "WHERE t.id = %s and t.network = %s and "
        "to_char(day, 'mmdd') != '0229' ORDER by day ASC",
        pgconn,
        params=(gddbase, gddceil, station, ctx["network"]),
        index_col=None,
    )
    # Now we need to join the frames
    df = pd.merge(df, climo, on="sday")
    df = df.sort_values("day", ascending=True)
    df = df.set_index("day")
    df["precip_diff"] = df["oprecip"] - df["cprecip"]
    df[glabel + "_diff"] = df["o" + glabel] - df["c" + glabel]

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    if whichplots == "all":
        fig = plt.figure(figsize=(9, 12))
        ax1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])
        ax2 = fig.add_axes(
            [0.1, 0.6, 0.8, 0.1], sharex=ax1, facecolor="#EEEEEE"
        )
        ax3 = fig.add_axes([0.1, 0.35, 0.8, 0.2], sharex=ax1)
        ax4 = fig.add_axes([0.1, 0.1, 0.8, 0.2], sharex=ax1)
        title = ("GDD(base=%.0f,ceil=%.0f), Precip, & " "SDD(base=86)") % (
            gddbase,
            gddceil,
        )
    elif whichplots == "gdd":
        fig = plt.figure()
        ax1 = fig.add_axes([0.14, 0.31, 0.8, 0.57])
        ax2 = fig.add_axes(
            [0.14, 0.11, 0.8, 0.2], sharex=ax1, facecolor="#EEEEEE"
        )
        title = ("GDD(base=%.0f,ceil=%.0f)") % (gddbase, gddceil)
    elif whichplots == "precip":
        fig = plt.figure()
        ax3 = fig.add_axes([0.1, 0.11, 0.8, 0.75])
        ax1 = ax3
        title = "Precipitation"
    elif whichplots == "sdd":
        fig = plt.figure()
        ax4 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax1 = ax4
        title = "Stress Degree Days (base=86)"

    ax1.set_title(
        ("Accumulated %s\n%s %s")
        % (title, station, ctx["_nt"].sts[station]["name"]),
        fontsize=18 if whichplots == "all" else 14,
    )

    for year in wantedyears:
        if year == 0:
            continue
        sts = sdate.replace(year=year)
        ets = sts + datetime.timedelta(days=(xlen - 1))
        color = yearcolors[wantedyears.index(year)]
        yearlabel = sts.year
        x = df.loc[sts:ets]
        if sts.year != ets.year:
            yearlabel = "%s-%s" % (sts.year, ets.year)
        if whichplots in ["gdd", "all"]:
            ax1.plot(
                range(len(x.index)),
                x[f"o{glabel}"].cumsum().values,
                zorder=6,
                color=color,
                label="%s" % (yearlabel,),
                lw=2,
            )
        # Get cumulated precip
        p = x["oprecip"].cumsum()
        if whichplots in ["all", "precip"]:
            ax3.plot(
                range(len(p.index)),
                p.values,
                color=color,
                lw=2,
                zorder=6,
                label="%s" % (yearlabel,),
            )
        p = x["osdd86"].cumsum()
        if whichplots in ["all", "sdd"]:
            ax4.plot(
                range(len(p.index)),
                p.values,
                color=color,
                lw=2,
                zorder=6,
                label="%s" % (yearlabel,),
            )

        # Plot Climatology
        if wantedyears.index(year) == 0:
            x = df.loc[sts:ets, "c" + glabel].cumsum()
            if whichplots in ["all", "gdd"]:
                ax1.plot(
                    range(len(x.index)),
                    x.values,
                    color="k",
                    label="Climatology",
                    lw=2,
                    zorder=5,
                )
            x = df.loc[sts:ets, "cprecip"].cumsum()
            if whichplots in ["all", "precip"]:
                ax3.plot(
                    range(len(x.index)),
                    x.values,
                    color="k",
                    label="Climatology",
                    lw=2,
                    zorder=5,
                )
            x = df.loc[sts:ets, "csdd86"].cumsum()
            if whichplots in ["all", "sdd"]:
                ax4.plot(
                    range(len(x.index)),
                    x.values,
                    color="k",
                    label="Climatology",
                    lw=2,
                    zorder=5,
                )

        x = df.loc[sts:ets, glabel + "_diff"].cumsum()
        if whichplots in ["all", "gdd"]:
            ax2.plot(
                range(len(x.index)),
                x.values,
                color=color,
                linewidth=2,
                linestyle="--",
            )

    xmin = np.nanmin(acc, 0)
    xmax = np.nanmax(acc, 0)
    if whichplots in ["all", "gdd"]:
        ax1.fill_between(range(len(xmin)), xmin, xmax, color="lightblue")
        ax1.grid(True)
        ax2.grid(True)
    xmin = np.nanmin(pacc, 0)
    xmax = np.nanmax(pacc, 0)
    if whichplots in ["all", "precip"]:
        ax3.fill_between(range(len(xmin)), xmin, xmax, color="lightblue")
        ax3.set_ylabel("Precipitation [inch]", fontsize=16)
        ax3.grid(True)
    xmin = np.nanmin(sacc, 0)
    xmax = np.nanmax(sacc, 0)
    if whichplots in ["all", "sdd"]:
        ax4.fill_between(range(len(xmin)), xmin, xmax, color="lightblue")
        ax4.set_ylabel(r"SDD Base 86 $^{\circ}\mathrm{F}$", fontsize=16)
        ax4.grid(True)

    if whichplots in ["all", "gdd"]:
        ax1.set_ylabel(
            (r"GDD Base %.0f Ceil %.0f $^{\circ}\mathrm{F}$")
            % (gddbase, gddceil),
            fontsize=16,
        )

        ax1.text(
            0.5,
            0.9,
            "%s/%s - %s/%s\nClimatology %s %.0f-%.0f"
            % (
                sdate.month,
                sdate.day,
                edate.month,
                edate.day,
                climosite,
                baseyear,
                datetime.date.today().year,
            ),
            transform=ax1.transAxes,
            ha="center",
            va="center",
        )

        ylim = ax2.get_ylim()
        spread = max([abs(ylim[0]), abs(ylim[1])]) * 1.1
        ax2.set_ylim(0 - spread, spread)
        ax2.text(
            0.0,
            1.0,
            "Accumulated Departure",
            transform=ax2.transAxes,
            bbox=dict(facecolor="white", ec="#EEEEEE", alpha=0.5),
            va="top",
            ha="left",
        )
        ax2.yaxis.tick_right()

    xticks = []
    xticklabels = []
    wanted = [1] if xlen > 31 else [1, 7, 15, 22, 29]
    now = sdate
    i = 0
    while now <= edate:
        if now.day in wanted:
            xticks.append(i)
            xticklabels.append(now.strftime("%-d\n%b"))
        now += datetime.timedelta(days=1)
        i += 1
    if whichplots in ["all", "gdd"]:
        ax2.set_xticks(xticks)
        ax2.set_xticklabels(xticklabels)
        ax1.legend(loc=2, prop={"size": 12})
        # Remove ticks on the top most plot
        for label in ax1.get_xticklabels():
            label.set_visible(False)

        ax1.set_xlim(0, xlen + 1)
    if whichplots in ["all", "precip"]:
        ax3.set_xticks(xticks)
        ax3.set_xticklabels(xticklabels)
        ax3.legend(loc=2, prop={"size": 10})
        ax3.set_xlim(0, xlen + 1)
    if whichplots in ["all", "sdd"]:
        ax4.set_xticks(xticks)
        ax4.set_xticklabels(xticklabels)
        ax4.legend(loc=2, prop={"size": 10})
        ax4.set_xlim(0, xlen + 1)

    return fig, df


if __name__ == "__main__":
    plotter(dict(station="AEEI4", network="ISUSM"))
