"""Temperature of rain"""
import calendar
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes, get_cmap
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart displays the frequency of having
    measurable precipitation reported by an ASOS site and the air temperature
    that was reported at the same time.  This chart makes an assumption
    about the two values being coincident, whereas in actuality they may not
    have been.
    """
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="AMW",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(type="cmap", name="cmap", default="jet", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """
            SELECT extract(week from valid) as week, tmpf from
            alldata WHERE station = %s and p01i > 0.009 and tmpf is not null
            and report_type = 3
        """,
            conn,
            params=(station,),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No data found.")

    sts = datetime.datetime(2012, 1, 1)
    xticks = []
    for i in range(1, 13):
        ts = sts.replace(month=i)
        xticks.append(int(ts.strftime("%j")))

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    title = (
        f"{ctx['_sname']} "
        f"({ab.year}-{datetime.date.today().year})\n"
        "Temperature Frequency During Precipitation by Week"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    bins = np.arange(df["tmpf"].min() - 5, df["tmpf"].max() + 5, 2)
    H, xedges, yedges = np.histogram2d(
        df["week"].values, df["tmpf"].values, [range(0, 54), bins]
    )
    rows = []
    for i, x in enumerate(xedges[:-1]):
        for j, y in enumerate(yedges[:-1]):
            rows.append(dict(tmpf=y, week=x, count=H[i, j]))
    resdf = pd.DataFrame(rows)

    years = datetime.date.today().year - ab.year
    H = np.ma.array(H) / float(years)
    H.mask = np.ma.where(H < 0.1, True, False)
    res = ax.pcolormesh(
        (xedges - 1) * 7,
        yedges,
        H.transpose(),
        cmap=get_cmap(ctx["cmap"]),
    )
    fig.colorbar(res, label="Hours per week per year")
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    y = []
    for i in range(np.shape(H)[0]):
        y.append(np.ma.sum(H[i, :] * (bins[:-1] + 0.5)) / np.ma.sum(H[i, :]))

    if np.nanmin(y) < 40:
        ax.axhline(32, ls="-.", color="r", lw=2)
        ax.text(180, 32, "32", ha="center", va="bottom", fontsize=14)
    ax.plot(xedges[:-1] * 7, y, zorder=3, lw=3, color="w")
    ax.plot(xedges[:-1] * 7, y, zorder=3, lw=1, color="k", label="Average")
    ax.legend(loc=2)

    ax.grid(True)
    ax.set_ylabel(r"Temperature [$^\circ$F]")

    return fig, resdf


if __name__ == "__main__":
    plotter({})
