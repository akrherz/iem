"""Daily avg wind speeds"""
import datetime

import numpy as np
import pandas as pd
from pandas.io.sql import read_sql
import matplotlib.patheffects as PathEffects
from pyiem.util import drct2text
from pyiem.util import get_autoplot_context, get_dbconnstr
from pyiem.plot import figure_axes
from pyiem.exceptions import NoDataFound
from metpy.units import units

PDICT = {
    "KT": "knots",
    "MPH": "miles per hour",
    "MPS": "meters per second",
    "KMH": "kilometers per hour",
}
XREF_UNITS = {
    "MPS": units("meter / second"),
    "KT": units("knot"),
    "KMH": units("kilometer / hour"),
    "MPH": units("mile / hour"),
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc["cache"] = 86400
    desc[
        "description"
    ] = """This plot displays daily average wind speeds for
    a given year and month of your choice.  These values are computed by the
    IEM using available observations.  Some observation sites explicitly
    produce an average wind speed, but that is not considered for this plot.
    You can download daily summary data
    <a href="/request/daily.phtml" class="alert-link">here</a>.
    The average wind direction
    is computed by vector averaging of the wind speed and direction reports.
    """
    desc["arguments"] = [
        dict(
            type="sid",
            name="zstation",
            default="DSM",
            network="IA_ASOS",
            label="Select Station:",
        ),
        dict(
            type="year",
            name="year",
            default=datetime.datetime.now().year,
            label="Select Year:",
        ),
        dict(
            type="month",
            name="month",
            default=datetime.datetime.now().month,
            label="Select Month:",
        ),
        dict(
            type="select",
            name="units",
            default="MPH",
            label="Wind Speed Units:",
            options=PDICT,
        ),
    ]
    return desc


def draw_line(ax, x, y, angle):
    """Draw a line"""
    r = 0.25
    ax.arrow(
        x,
        y,
        r * np.cos(angle),
        r * np.sin(angle),
        head_width=0.35,
        head_length=0.5,
        fc="k",
        ec="k",
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    plot_units = ctx["units"]
    year = ctx["year"]
    month = ctx["month"]
    sts = datetime.date(year, month, 1)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)

    df = read_sql(
        """
        SELECT day, avg_sknt as sknt, vector_avg_drct as drct
        from summary s JOIN stations t
        ON (t.iemid = s.iemid) WHERE t.id = %s and t.network = %s and
        s.day >= %s and s.day < %s and avg_sknt is not null
        and vector_avg_drct is not null ORDER by day ASC
    """,
        get_dbconnstr("iem"),
        params=(station, ctx["network"], sts, ets),
    )
    if df.empty:
        raise NoDataFound("ERROR: No Data Found")
    df["day"] = pd.to_datetime(df["day"])
    sknt = (df["sknt"].values * units("knot")).to(XREF_UNITS[plot_units]).m
    title = (
        f"{ctx['_nt'].sts[station]['name']} [{station}]\n"
        f"{sts:%b %Y} Daily Average Wind Speed and Direction"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)
    ax.bar(
        df["day"].dt.day.values, sknt, ec="green", fc="green", align="center"
    )
    pos = max([min(sknt) / 2.0, 0.5])
    for d, _, r in zip(df["day"].dt.day.values, sknt, df["drct"].values):
        draw_line(ax, d, max(sknt) + 0.5, (270.0 - r) / 180.0 * np.pi)
        txt = ax.text(
            d,
            pos,
            drct2text(r),
            ha="center",
            rotation=90,
            color="white",
            va="center",
        )
        txt.set_path_effects(
            [PathEffects.withStroke(linewidth=2, foreground="k")]
        )
    ax.grid(True, zorder=11)
    ax.set_xlim(0.5, 31.5)
    ax.set_xticks(range(1, 31, 5))
    ax.set_ylim(top=max(sknt) + 2)

    ax.set_ylabel(f"Average Wind Speed [{PDICT[plot_units]}]")

    return fig, df


if __name__ == "__main__":
    plotter({})
