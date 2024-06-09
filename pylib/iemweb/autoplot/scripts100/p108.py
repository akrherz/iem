"""
This plot presents accumulated totals and departures
of growing degree days (GDD), precipitation and stress degree days (SDD).
Leap days
are not considered for this plot. The light blue area represents the
range of accumulated values based on the observation history at the
site.
"""

import datetime

import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context

PDICT = {
    "all": "Show All Three Plots",
    "gdd": "Show just Growing Degree Days",
    "precip": "Show just Precipitation",
    "sdd": "Show just Stress Degree Days",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    if today.month < 5:
        today = today.replace(year=today.year - 1, month=10, day=1)
    sts = today.replace(month=5, day=1)

    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
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
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    if edate < sdate:
        sdate, edate = edate, sdate
    if f"{sdate:%m%d}" == "0229":
        sdate = sdate.replace(day=1)
    year2 = ctx.get("year2", 0)
    year3 = ctx.get("year3", 0)
    year4 = ctx.get("year4", 0)
    wantedyears = [sdate.year, year2, year3, year4]
    yearcolors = ["r", "g", "b", "purple"]
    gddbase = ctx["base"]
    gddceil = ctx["ceil"]
    whichplots = ctx["which"]
    glabel = f"gdd{gddbase}{gddceil}"
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            f"""
        WITH avgs as (
            SELECT sday, avg(gddxx(%s, %s, high, low)) as c{glabel},
            avg(sdd86(high, low)) as csdd86, avg(precip) as cprecip
            from alldata WHERE station = %s GROUP by sday
        )
        SELECT day, gddxx(%s, %s, high, low) as o{glabel}, c{glabel},
        o.precip as oprecip, cprecip,
        sdd86(o.high, o.low) as osdd86, csdd86 from alldata o
        JOIN avgs a on (o.sday = a.sday)
        WHERE station = %s and o.sday != '0229' ORDER by day ASC
        """,
            conn,
            params=(gddbase, gddceil, station, gddbase, gddceil, station),
            index_col="day",
        )
    df["precip_diff"] = df["oprecip"] - df["cprecip"]
    df[glabel + "_diff"] = df["o" + glabel] - df["c" + glabel]

    xlen = int((edate - sdate).days) + 1  # In case of leap day
    years = (datetime.datetime.now().year - ab.year) + 1
    acc = np.zeros((years, xlen))
    acc[:] = np.nan
    pacc = np.zeros((years, xlen))
    pacc[:] = np.nan
    sacc = np.zeros((years, xlen))
    sacc[:] = np.nan
    if whichplots == "all":
        fig = figure(figsize=(9, 12), apctx=ctx)
        ax1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])
        ax2 = fig.add_axes(
            [0.1, 0.6, 0.8, 0.1], sharex=ax1, facecolor="#EEEEEE"
        )
        ax3 = fig.add_axes([0.1, 0.35, 0.8, 0.2], sharex=ax1)
        ax4 = fig.add_axes([0.1, 0.1, 0.8, 0.2], sharex=ax1)
        title = (
            f"GDD(base={gddbase:.0f},ceil={gddceil:.0f}), Precip, & "
            "SDD(base=86)"
        )
    elif whichplots == "gdd":
        fig = figure(apctx=ctx)
        ax1 = fig.add_axes([0.14, 0.31, 0.8, 0.57])
        ax2 = fig.add_axes(
            [0.14, 0.11, 0.8, 0.2], sharex=ax1, facecolor="#EEEEEE"
        )
        title = f"GDD(base={gddbase:.0f},ceil={gddceil:.0f})"
    elif whichplots == "precip":
        fig = figure(apctx=ctx)
        ax3 = fig.add_axes([0.1, 0.11, 0.8, 0.75])
        ax1 = ax3
        title = "Precipitation"
    else:  # sdd
        fig = figure(apctx=ctx)
        ax4 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax1 = ax4
        title = "Stress Degree Days (base=86)"

    ax1.set_title(
        (
            f"Accumulated {title}\n"
            f"{station} {ctx['_nt'].sts[station]['name']}"
        ),
        fontsize=18 if whichplots == "all" else 14,
    )

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    for year in range(ab.year, datetime.datetime.now().year + 1):
        sts = sdate.replace(year=year)
        ets = sts + datetime.timedelta(days=xlen - 1)
        x = df.loc[sts:ets, f"o{glabel}"].cumsum()
        if x.empty:
            continue
        acc[(year - sdate.year), : len(x.index)] = x.values
        x = df.loc[sts:ets, "oprecip"].cumsum()
        pacc[(year - sdate.year), : len(x.index)] = x.values
        x = df.loc[sts:ets, "osdd86"].cumsum()
        sacc[(year - sdate.year), : len(x.index)] = x.values

        if year not in wantedyears:
            continue
        color = yearcolors[wantedyears.index(year)]
        yearlabel = sts.year
        if sts.year != ets.year:
            yearlabel = f"{sts.year}-{ets.year}"
        if whichplots in ["gdd", "all"]:
            ax1.plot(
                range(len(x.index)),
                df.loc[sts:ets, "o" + glabel].cumsum().values,
                zorder=6,
                color=color,
                label=f"{yearlabel}",
                lw=2,
            )
        # Get cumulated precip
        p = df.loc[sts:ets, "oprecip"].cumsum()
        if whichplots in ["all", "precip"]:
            ax3.plot(
                range(len(p.index)),
                p.values,
                color=color,
                lw=2,
                zorder=6,
                label=f"{yearlabel}",
            )
        p = df.loc[sts:ets, "osdd86"].cumsum()
        if whichplots in ["all", "sdd"]:
            ax4.plot(
                range(len(p.index)),
                p.values,
                color=color,
                lw=2,
                zorder=6,
                label=f"{yearlabel}",
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
            f"GDD Base {gddbase:.0f} Ceil {gddceil:.0f} "
            r"$^{\circ}\mathrm{F}$",
            fontsize=16,
        )

        ax1.text(
            0.5,
            0.9,
            f"{sdate.month}/{sdate.day} - {edate.month}/{edate.day}",
            transform=ax1.transAxes,
            ha="center",
        )

        ylim = ax2.get_ylim()
        spread = max([abs(ylim[0]), abs(ylim[1])]) * 1.1
        ax2.set_ylim(0 - spread, spread)
        ax2.text(
            0.02,
            0.1,
            " Accumulated Departure ",
            transform=ax2.transAxes,
            bbox=dict(facecolor="white", ec="#EEEEEE"),
        )
        ax2.yaxis.tick_right()

    xticks = []
    xticklabels = []
    wanted = [1] if xlen > 60 else [1, 7, 15, 22, 29]
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
