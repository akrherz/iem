"""
This chart displays the combination of average
temperature and total precipitation for one or more months of your choice.
The dots are colorized based on the Southern Oscillation Index (SOI) value
for a month of your choice.  Many times, users want to compare the SOI
value with monthly totals for a period a few months after the validity of
the SOI value.  The thought is that there is some lag time for the impacts
of a given SOI to be felt in the midwestern US.
"""
import datetime

import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
import psycopg2.extras
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure, get_cmap
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from scipy import stats

PDICT = {"none": "Show all values", "hide": 'Show "strong" events'}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IA0000",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(type="month", name="month", default=9, label="Start Month:"),
        dict(
            type="int",
            name="months",
            default=2,
            label="Number of Months to Average:",
        ),
        dict(
            type="int",
            name="lag",
            default=-3,
            label="Number of Months to Lag for SOI Value:",
        ),
        dict(
            type="select",
            name="h",
            default="none",
            options=PDICT,
            label="Hide/Show week SOI events -0.5 to 0.5",
        ),
        dict(
            type="text",
            default=str(datetime.date.today().year),
            name="year",
            label="Year(s) to Highlight in Chart (comma delimited)",
        ),
        dict(type="cmap", name="cmap", default="RdYlGn", label="Color Ramp:"),
    ]
    return desc


def title(wanted):
    """Make a title"""
    t1 = datetime.date(2000, wanted[0], 1)
    t2 = datetime.date(2000, wanted[-1], 1)
    return "Avg Precip + Temp for %s%s" % (
        t1.strftime("%B"),
        " thru %s" % (t2.strftime("%B"),) if wanted[0] != wanted[-1] else "",
    )


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ccursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    lagmonths = ctx["lag"]
    months = ctx["months"]
    month = ctx["month"]
    highyears = [int(x) for x in ctx["year"].split(",")]
    h = ctx["h"]

    wantmonth = month + lagmonths
    yearoffset = 0
    if month + lagmonths < 1:
        wantmonth = 12 - (month + lagmonths)
        yearoffset = 1

    wanted = []
    deltas = []
    for m in range(month, month + months):
        if m < 13:
            wanted.append(m)
            deltas.append(0)
        else:
            wanted.append(m - 12)
            deltas.append(-1)

    elnino = {}
    ccursor.execute("SELECT monthdate, soi_3m, anom_34 from elnino")
    for row in ccursor:
        if row[0].month != wantmonth:
            continue
        elnino[row[0].year + yearoffset] = dict(soi_3m=row[1], anom_34=row[2])

    ccursor.execute(
        "SELECT year, month, sum(precip), avg((high+low)/2.) "
        "from alldata where station = %s GROUP by year, month",
        (station,),
    )
    if ccursor.rowcount == 0:
        raise NoDataFound("No Data Found.")
    yearly = {}
    for row in ccursor:
        (_year, _month, _precip, _temp) = row
        if _month not in wanted:
            continue
        effectiveyear = _year + deltas[wanted.index(_month)]
        nino = elnino.get(effectiveyear, {}).get("soi_3m", None)
        if nino is None:
            continue
        data = yearly.setdefault(
            effectiveyear, dict(precip=0, temp=[], nino=nino)
        )
        data["precip"] += _precip
        data["temp"].append(float(_temp))

    title2 = f"{ctx['_sname']} :: {title(wanted)}"
    subtitle = "%s SOI (3 month average)" % (
        datetime.date(2000, wantmonth, 1).strftime("%B"),
    )
    fig = figure(title=title2, subtitle=subtitle, apctx=ctx)
    ax = fig.add_axes([0.07, 0.12, 0.53, 0.75])

    cmap = get_cmap(ctx["cmap"])
    zdata = np.arange(-2.0, 2.1, 0.5)
    norm = mpcolors.BoundaryNorm(zdata, cmap.N)
    rows = []
    xs = []
    ys = []
    for year, item in yearly.items():
        x = item["precip"]
        y = np.average(item["temp"])
        xs.append(x)
        ys.append(y)
        val = yearly[year]["nino"]
        c = cmap(norm([val])[0])
        if h == "hide" and -0.5 < val < 0.5:
            ax.scatter(
                x,
                y,
                facecolor="#EEEEEE",
                edgecolor="#EEEEEE",
                s=30,
                zorder=2,
                marker="s",
            )
        else:
            ax.scatter(
                x, y, facecolor=c, edgecolor="k", s=60, zorder=3, marker="o"
            )
        if year in highyears:
            ax.text(x, y + 0.2, f"{year}", ha="center", va="bottom", zorder=5)
        rows.append(dict(year=year, precip=x, tmpf=y, soi3m=val))

    if not rows:
        raise NoDataFound("Failed to find any data.")
    df = pd.DataFrame(rows)
    ax.axhline(np.average(ys), lw=2, color="k", linestyle="-.", zorder=2)
    ax.axvline(np.average(xs), lw=2, color="k", linestyle="-.", zorder=2)

    sm = plt.cm.ScalarMappable(norm, cmap)
    sm.set_array(zdata)
    cb = fig.colorbar(sm, extend="both")
    cb.set_label("<-- El Nino :: SOI :: La Nina -->")

    ax.grid(True)
    ax.set_xlim(left=-0.01)
    ax.set_xlabel("Total Precipitation [inch], Avg: %.2f" % (np.average(xs),))
    ax.set_ylabel(
        (r"Average Temperature $^\circ$F, " "Avg: %.1f") % (np.average(ys),)
    )
    ax2 = fig.add_axes([0.67, 0.55, 0.28, 0.35])
    ax2.scatter(df["soi3m"].values, df["tmpf"].values)
    ax2.set_xlabel("<-- El Nino :: SOI :: La Nina -->")
    ax2.set_ylabel(r"Avg Temp $^\circ$F")
    slp, intercept, r_value, _, _ = stats.linregress(
        df["soi3m"].values, df["tmpf"].values
    )
    y1 = -2.0 * slp + intercept
    y2 = 2.0 * slp + intercept
    ax2.plot([-2, 2], [y1, y2])
    ax2.text(
        0.97,
        0.9,
        "R$^2$=%.2f" % (r_value**2,),
        ha="right",
        transform=ax2.transAxes,
        bbox=dict(color="white"),
    )
    ax2.grid(True)

    ax3 = fig.add_axes([0.67, 0.1, 0.28, 0.35])
    ax3.scatter(df["soi3m"].values, df["precip"].values)
    ax3.set_xlabel("<-- El Nino :: SOI :: La Nina -->")
    ax3.set_ylabel("Total Precip [inch]")
    slp, intercept, r_value, _, _ = stats.linregress(
        df["soi3m"].values, df["precip"].values
    )
    y1 = -2.0 * slp + intercept
    y2 = 2.0 * slp + intercept
    ax3.plot([-2, 2], [y1, y2])
    ax3.text(
        0.97,
        0.9,
        f"R$^2$={(r_value**2):.2f}",
        ha="right",
        transform=ax3.transAxes,
        bbox=dict(color="white"),
    )
    ax3.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter({})
