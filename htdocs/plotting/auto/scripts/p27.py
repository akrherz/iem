"""
This chart presents the date of the first fall
(date after 1 July) temperature below threshold 1 and then the number of
days after that date until threshold 2 was reached. The slanted dashed
lines are used to translate the dots to the date of occurrence for the
second threshold.
"""
import datetime

import numpy as np
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from scipy.stats import linregress


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATAME",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="int", name="t1", default=32, label="Temperature Threshold 1:"
        ),
        dict(
            type="int", name="t2", default=29, label="Temperature Threshold 2:"
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    station = ctx["station"]
    t1 = ctx["t1"]
    t2 = ctx["t2"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT year,
            min(low) as min_low,
            min(case when low < %s then extract(doy from day)
                else 999 end) as t1_doy,
            min(case when low < %s then extract(doy from day)
                else 999 end) as t2_doy
            from alldata where station = %s and month > 6
            GROUP by year ORDER by year ASC
        """,
            conn,
            params=(t1, t2, station),
            index_col="year",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df = df[df["t2_doy"] < 400]

    doy = np.array(df["t1_doy"], "i")
    doy2 = np.array(df["t2_doy"], "i")

    sts = datetime.datetime(2000, 1, 1)
    xticks = []
    xticklabels = []
    for i in range(min(doy), max(doy2) + 1):
        ts = sts + datetime.timedelta(days=i)
        if ts.day in [1, 8, 15, 22]:
            xticks.append(i)
            fmt = "%b %-d" if ts.day == 1 else "%-d"
            xticklabels.append(ts.strftime(fmt))

    title = f"{ctx['_sname']}\nFirst Fall Temperature Occurences"
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.scatter(doy, doy2 - doy)

    for x in xticks:
        ax.plot((x - 100, x), (100, 0), ":", c=("#000000"))

    h_slope, intercept, r_value, _, _ = linregress(
        df["t1_doy"].values, df["t2_doy"].values - df["t1_doy"].values
    )
    x = np.array(ax.get_xlim())
    ax.plot(x, h_slope * x + intercept, lw=2, color="r")
    ax.text(
        0.95,
        0.91,
        f"slope: {h_slope:.2f} days/day, R$^2$={(r_value**2):.2f}",
        bbox=dict(color="white"),
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        color="r",
    )

    ax.set_ylim(-1, max(doy2 - doy) + 4)
    ax.set_xlim(min(doy) - 4, max(doy) + 4)
    ax.set_ylabel(f"Days until first sub {t2}" r"$^{\circ}\mathrm{F}$")
    ax.set_xlabel(f"First day of sub {t1}" r"$^{\circ}\mathrm{F}$")

    ax.grid(True)

    return fig, df


if __name__ == "__main__":
    plotter({})
