"""
This chart displays either the first or last date
of the winter season with a snowfall of a given intensity.  The snowfall
and snow depth data is not of great quality, so please be careful with
this plot.

<p>For a `Trace` snowfall event to count, the coincident low temperature needs
to be below 40F. This is to help filter out hail events.</p>
"""

import calendar
import datetime

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.database import get_dbconn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_autoplot_context

PDICT = {
    "first": "First Snowfall after 1 July",
    "last": "Last Snowfall before 1 July",
}
XS = np.array([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
XS = np.concatenate([XS, XS + 366])


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station:",
            network="IACLIMATE",
        ),
        dict(
            type="text",
            name="threshold",
            default="1",
            label="First Snowfall Threshold (T for trace)",
        ),
        dict(
            type="select",
            name="dir",
            default="last",
            options=PDICT,
            label="Which Variable to Plot?",
        ),
    ]
    return desc


def get_data(ctx):
    """Get some data please"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    station = ctx["station"]
    threshold = ctx["threshold"]
    threshold = TRACE_VALUE if threshold in ["T", "t"] else float(threshold)

    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("No Data Found.")
    syear = max(1893, ab.year)
    eyear = datetime.datetime.now().year

    snow = np.zeros((eyear - syear + 1, 366))
    snowd = np.zeros((eyear - syear + 1, 366))
    cursor.execute(
        """
        SELECT extract(doy from day), year,
        case when snow > 0 and snow < 0.09 and low >= 40 then 0 else snow end,
        snowd from alldata where station = %s and year >= %s
        """,
        (station, syear),
    )
    for row in cursor:
        # On non-leap year, duplicate our snowdepth on 31 Dec
        if row[0] == 365 and not calendar.isleap(row[1]):
            snowd[row[1] - syear, int(row[0])] = row[3]
        snow[row[1] - syear, int(row[0] - 1)] = row[2]
        snowd[row[1] - syear, int(row[0] - 1)] = row[3]
    pgconn.close()
    # reset any nan
    snow = np.where(np.isnan(snow), 0, snow)
    snowd = np.where(np.isnan(snowd), -1, snowd)

    rows = []
    for i, year in enumerate(range(syear, eyear)):
        # Slap the years together so we cross over 1 Jan
        snowfall = tuple(snow[i, 183:]) + tuple(snow[i + 1, :183])
        snowdepth = tuple(snowd[i, 183:]) + tuple(snowd[i + 1, :183])
        hits = np.where(np.array(snowfall) >= threshold)[0]
        if hits.size == 0:
            continue
        idx = hits[0] if ctx["dir"] == "first" else hits[-1]
        # Check that we have snowd for this index, if not, DQ
        if snowdepth[idx] < 0:
            continue
        # Compute how long this stuck around
        sfree = idx + 1
        for sfree in range(idx + 1, 366):
            if snowdepth[sfree] <= 0.01:
                break
        days = sfree - idx
        if days >= 30:
            color = "purple"
        elif days >= 11:
            color = "g"
        elif days >= 3:
            color = "b"
        else:
            color = "r"
        dt = datetime.date(year, 1, 1) + datetime.timedelta(
            days=(int(idx) + 183 - 1)
        )
        rows.append(
            dict(
                year=year,
                snow_date=dt,
                snow_doy=(idx + 183),
                color=color,
                days=days,
                snowfree_doy=(sfree + 183),
                snowfall=snowfall[idx],
            )
        )

    return pd.DataFrame(rows)


def plot_yearly_trend(fig, df):
    """Plot the yearly trend"""
    ax = fig.add_axes([0.55, 0.15, 0.43, 0.75])
    x = df["year"].values
    y = df["snow_doy"].values
    ax.scatter(x, y)
    ax.set_xlim(df["year"].min() - 1, df["year"].max() + 1)
    ax.set_ylabel("Date")
    ax.grid(True)
    ax.set_yticks(XS)
    ax.set_yticklabels(calendar.month_abbr[1:] + calendar.month_abbr[1:])
    ax.set_ylim(df["snow_doy"].min() - 5, df["snowfree_doy"].max() + 5)
    ax.set_xlabel("Year")
    # Add a moving 30 year average
    ax.plot(
        df["year"].values,
        df["snow_doy"].rolling(window=30, center=False).mean(),
        lw=2,
        color="r",
        label="30 year trailing mean",
    )
    # Add a trend line
    xmean = np.mean(x)
    ymean = np.mean(y)
    xdiff = x - xmean
    ydiff = y - ymean
    slope = np.sum(xdiff * ydiff) / np.sum(xdiff * xdiff)
    yint = ymean - slope * xmean
    ax.plot(
        x,
        slope * x + yint,
        lw=2,
        color="k",
        label=f"Trend: {(slope * 10):.2f} days / decade",
    )
    ax.legend(loc=(0.0, -0.15), ncol=2)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    df = get_data(ctx)
    t1 = "Last" if ctx["dir"] == "last" else "First"
    t2 = (
        "Trace+"
        if ctx["threshold"] == "T"
        else f"{float(ctx['threshold']):.2f}+ Inch"
    )
    title = (
        f"{ctx['_sname']}:: {t1} {t2} Snowfall "
        f"({df['year'].min()}-{df['year'].max()})\n"
        "(color is how long snow remained)"
    )
    fig = figure(title=title, apctx=ctx)
    plot_yearly_trend(fig, df)
    ax = fig.add_axes([0.08, 0.11, 0.36, 0.79])

    ax.scatter(
        df["snow_doy"],
        df["snowfall"],
        facecolor=df["color"],
        edgecolor=df["color"],
        s=100,
    )
    for _, row in df.iterrows():
        ax.scatter(
            row["snowfree_doy"],
            row["snowfall"],
            marker="x",
            s=100,
            color=row["color"],
        )
        ax.plot(
            [row["snow_doy"], row["snowfree_doy"]],
            [row["snowfall"], row["snowfall"]],
            lw="2",
            color=row["color"],
        )
    ax.set_xticks(XS)
    ax.set_xticklabels(calendar.month_abbr[1:] + calendar.month_abbr[1:])
    ax.grid(True)
    ax.set_ylim(bottom=0)
    ax2 = ax.twinx()
    ptile = np.percentile(df["snow_doy"].values, np.arange(100))
    ax2.plot(ptile, np.arange(100), lw=2, color="k")
    ax2.set_ylabel(
        ("Frequency of %s Date (CDF) [%%] (black line)")
        % ("Start" if ctx["dir"] == "first" else "Last",)
    )
    ax.set_ylabel("Snowfall [inch], Avg: %.1f inch" % (df["snowfall"].mean(),))
    p0 = Rectangle((0, 0), 1, 1, fc="purple")
    p1 = Rectangle((0, 0), 1, 1, fc="g")
    p2 = Rectangle((0, 0), 1, 1, fc="b")
    p3 = Rectangle((0, 0), 1, 1, fc="r")
    ax.legend(
        (p0, p1, p2, p3),
        (
            "> 31 days [%s]" % (len(df[df["color"] == "purple"].index),),
            "10 - 31 [%s]" % (len(df[df["color"] == "g"].index),),
            "3 - 10 [%s]" % (len(df[df["color"] == "b"].index),),
            "< 3 days [%s]" % (len(df[df["color"] == "r"].index),),
        ),
        ncol=2,
        fontsize=11,
        loc=(0.0, -0.15),
    )
    ax.set_xlim(df["snow_doy"].min() - 5, df["snowfree_doy"].max() + 5)

    box = ax.get_position()
    ax.set_position(
        [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
    )
    ax2.set_position(
        [box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9]
    )
    ax2.set_yticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
    ax2.set_ylim(0, 101)
    df = df.set_index("year").drop(columns=["color"])
    return fig, df
