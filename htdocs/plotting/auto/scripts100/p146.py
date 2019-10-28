"""Temperature of rain"""
import datetime
import calendar

import numpy as np
from pandas.io.sql import read_sql
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
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
    """ Go """
    pgconn = get_dbconn("asos")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]

    df = read_sql(
        """
    WITH obs as (
        SELECT date_trunc('hour', valid) as t, avg(tmpf) as avgt from alldata
        WHERE station = %s and p01i >= 0.01 and tmpf is not null
        GROUP by t
    )

    SELECT extract(week from t) as week, avgt from obs
    """,
        pgconn,
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

    (fig, ax) = plt.subplots(1, 1, figsize=(8, 6))

    bins = np.arange(df["avgt"].min() - 5, df["avgt"].max() + 5, 2)
    H, xedges, yedges = np.histogram2d(
        df["week"].values, df["avgt"].values, [range(0, 54), bins]
    )
    rows = []
    for i, x in enumerate(xedges[:-1]):
        for j, y in enumerate(yedges[:-1]):
            rows.append(dict(tmpf=y, week=x, count=H[i, j]))
    resdf = pd.DataFrame(rows)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    years = datetime.date.today().year - ab.year
    H = np.ma.array(H) / float(years)
    H.mask = np.ma.where(H < 0.1, True, False)
    res = ax.pcolormesh(
        (xedges - 1) * 7, yedges, H.transpose(), cmap=plt.get_cmap(ctx["cmap"])
    )
    fig.colorbar(res, label="Hours per week per year")
    ax.set_xticks(xticks)
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xlim(0, 366)

    y = []
    for i in range(np.shape(H)[0]):
        y.append(np.ma.sum(H[i, :] * (bins[:-1] + 0.5)) / np.ma.sum(H[i, :]))

    ax.plot(xedges[:-1] * 7, y, zorder=3, lw=3, color="w")
    ax.plot(xedges[:-1] * 7, y, zorder=3, lw=1, color="k", label="Average")
    ax.legend(loc=2)

    ax.set_title(
        (
            "[%s] %s (%s-%s)\n"
            "Temperature Frequency During Precipitation by Week"
        )
        % (
            station,
            ctx["_nt"].sts[station]["name"],
            ab.year,
            datetime.date.today().year,
        )
    )
    ax.grid(True)
    ax.set_ylabel(r"Temperature [$^\circ$F]")

    return fig, resdf


if __name__ == "__main__":
    plotter(dict())
