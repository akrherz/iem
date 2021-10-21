"""temps vs high and low"""
import calendar

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This chart presents violin plots of the distribution of daily
    high and low temperatures on dates with and without snow cover by month.
    A given month is plotted when at least 1% of the days on record for the
    month had snowcover.  There
    are a number of caveats due to the timing of the daily temperature and
    snow cover report.  Also with the quality of the snow cover data."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        )
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"].upper()
    table = "alldata_%s" % (station[:2],)
    # Load all available data
    df = read_sql(
        f"SELECT year, month, high, low, snowd from {table} WHERE "
        "station = %s and snowd is not null",
        pgconn,
        params=(station,),
        index_col=None,
    )
    if df.empty:
        raise NoDataFound("No data found.")

    # Consider months that have at least 3% of days with snowcover
    total = df.groupby("month").count()
    coverdf = df[df["snowd"] > 0]
    nocoverdf = df[df["snowd"] == 0]
    snowcover = coverdf.groupby("month").count()
    freq = snowcover["snowd"] / total["snowd"]
    monthsall = freq[freq > 0.03].index.values.tolist()
    # Sort the months to place fall first
    months = [x for x in monthsall if x > 6]
    months2 = [x for x in monthsall if x < 7]
    months.extend(months2)

    fig = plt.figure()
    ax = [
        fig.add_axes([0.12, 0.56, 0.83, 0.32]),
        fig.add_axes([0.12, 0.1, 0.83, 0.32]),
    ]
    colors = ["r", "b"]
    res = []
    for i, lbl in enumerate(["high", "low"]):
        for j, month in enumerate(months):
            vopts = dict(
                positions=[j], showmeans=False, showextrema=False, widths=0.8
            )

            # RHS
            vals = coverdf[coverdf["month"] == month][lbl]
            v = ax[i].violinplot(vals, **vopts)
            meanval2 = vals.mean()
            ax[i].plot([j, j + 0.4], [meanval2, meanval2], c=colors[1])
            ax[i].text(
                j, meanval2, rf"{meanval2:.0f}$^\circ$", c=colors[1], ha="left"
            )
            b = v["bodies"][0]
            m = np.mean(b.get_paths()[0].vertices[:, 0])
            b.get_paths()[0].vertices[:, 0] = np.clip(
                b.get_paths()[0].vertices[:, 0], m, np.inf
            )
            b.set_color(colors[1])

            # LHS
            vals = nocoverdf[nocoverdf["month"] == month][lbl]
            meanval = vals.mean()
            if not vals.empty:
                v = ax[i].violinplot(vals, **vopts)
                ax[i].plot([j - 0.4, j], [meanval, meanval], c=colors[0])
                ax[i].text(
                    j,
                    meanval,
                    rf"{meanval:.0f}$^\circ$",
                    c=colors[0],
                    ha="right",
                )
                b = v["bodies"][0]
                m = np.mean(b.get_paths()[0].vertices[:, 0])
                b.get_paths()[0].vertices[:, 0] = np.clip(
                    b.get_paths()[0].vertices[:, 0], -np.inf, m
                )
                b.set_color(colors[0])

            res.append(
                {
                    "month": month,
                    f"{lbl}_withoutsnow": meanval,
                    f"{lbl}_withsnow": meanval2,
                }
            )

        ax[i].set_xticks(range(len(months)))
        ax[i].set_xticklabels([calendar.month_abbr[m] for m in months])
        ax[i].grid(axis="y")
        ax[i].axhline(32, ls="--", color="purple", alpha=0.8, lw=0.5)
        ax[i].text(len(months) - 0.3, 32, r"32$^\circ$", color="purple")

    pr0 = plt.Rectangle((0, 0), 1, 1, fc="r")
    pr1 = plt.Rectangle((0, 0), 1, 1, fc="b")
    ax[0].legend(
        (pr0, pr1),
        ("Without Snow Cover", "With Snow Cover"),
        ncol=2,
        loc=(0.1, -0.35),
    )

    ax[0].set_title(
        ("%s [%s]\nDaily Temp Distributions by Month by Snow Cover[%s-%s]")
        % (
            ctx["_nt"].sts[station]["name"],
            station,
            df["year"].min(),
            df["year"].max(),
        )
    )
    ax[0].set_ylabel(r"Daily High Temp $^\circ$F")
    ax[1].set_ylabel(r"Daily Low Temp $^\circ$F")

    return fig, pd.DataFrame(res)


if __name__ == "__main__":
    plotter(dict(station="MNTINL", network="MNCLIMATE"))
