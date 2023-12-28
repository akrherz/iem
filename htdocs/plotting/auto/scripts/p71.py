"""
This plot displays daily average wind speeds for
a given year and month of your choice.  These values are computed by the
IEM using available observations.  Some observation sites explicitly
produce an average wind speed, but that is not considered for this plot.
You can download daily summary data
<a href="/request/daily.phtml" class="alert-link">here</a>.
The average wind direction
is computed by vector averaging of the wind speed and direction reports.
"""
import datetime

import matplotlib.patheffects as PathEffects
import numpy as np
import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import (
    convert_value,
    drct2text,
    get_autoplot_context,
    get_sqlalchemy_conn,
)

PDICT = {
    "KT": "knots",
    "MPH": "miles per hour",
    "MPS": "meters per second",
    "KMH": "kilometers per hour",
}
XREF_UNITS = {
    "MPS": "meter / second",
    "KT": "knot",
    "KMH": "kilometer / hour",
    "MPH": "mile / hour",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
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


def arrow(ax, x, y, angle):
    """Draw a arrow."""
    # This is suboptimal as it is in data space and not an annotation space
    r = 0.25
    ax.arrow(
        x,
        y,
        r * np.cos(angle),
        r * np.sin(angle),
        head_width=0.35,
        head_length=0.35,
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
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
                SELECT extract(year from day) as year,
                to_char(day, 'mmdd') as sday,
                day, avg_sknt as sknt, vector_avg_drct as drct
                from summary s WHERE iemid = %s and
                extract(month from day) = %s and avg_sknt is not null
                and vector_avg_drct is not null ORDER by day ASC
        """,
            conn,
            params=(ctx["_nt"].sts[station]["iemid"], month),
            parse_dates=["day"],
        )
    title = (
        f"{ctx['_sname']}\n"
        f"{sts:%b %Y} Daily Average Wind Speed and Direction"
    )
    (fig, ax) = figure_axes(title=title, apctx=ctx)

    if not df.empty:
        # Convert speed to desired units
        df["speed"] = convert_value(df["sknt"], "knot", XREF_UNITS[plot_units])
        # compute climatology
        climo = (
            df[["speed", "sday"]]
            .groupby("sday")
            .mean()
            .rolling(window=7, center=True, min_periods=1)
            .mean()
            .reset_index()
        )
        climo["day_of_month"] = climo["sday"].apply(lambda x: int(x[-2:]))
        label = (
            f"Smoothed Climatology ({df['year'].min():.0f}-"
            f"{df['year'].max():.0f})"
        )
        # Get this year's data
        df = df[df["year"] == year]
        if not df.empty:
            ax.bar(
                df["day"].dt.day.values,
                df["speed"].values,
                ec="green",
                fc="green",
                align="center",
            )
            pos = max([df["speed"].min() / 2.0, 0.5])
            # Leave 15% room at the top
            apos = df["speed"].max() * 1.075
            for _, row in df.iterrows():
                x = row["day"].day
                arrow(ax, x, apos, (270.0 - row["drct"]) / 180.0 * np.pi)
                ax.text(
                    x,
                    pos,
                    drct2text(row["drct"]),
                    ha="center",
                    rotation=90,
                    color="white",
                    va="center",
                ).set_path_effects(
                    [PathEffects.withStroke(linewidth=2, foreground="k")]
                )
            ax.set_ylim(0, df["speed"].max() * 1.15)
            ax.plot(
                climo["day_of_month"],
                climo["speed"],
                "k-",
                lw=2,
                label=label,
            )
            ax.legend(loc=(0.5, -0.1))
        ax.grid(True, zorder=11)
    else:
        ax.text(
            0.5,
            0.5,
            "No Wind Speed Information For Site For Period.",
            transform=ax.transAxes,
            ha="center",
            bbox={"color": "white"},
        )
    ax.set_xlim(0.5, 31.5)
    ax.set_xticks(range(1, 31, 5))

    ax.set_ylabel(f"Average Wind Speed [{PDICT[plot_units]}]")

    return fig, df


if __name__ == "__main__":
    plotter({})
