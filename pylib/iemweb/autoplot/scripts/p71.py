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

from datetime import date, datetime

import matplotlib.patheffects as PathEffects
import pandas as pd
from matplotlib.axes import Axes
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.plot import figure
from pyiem.util import convert_value, drct2text

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
            default=datetime.now().year,
            label="Select Year:",
        ),
        dict(
            type="month",
            name="month",
            default=datetime.now().month,
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


def pprint(value: float) -> str:
    """Return a pretty printed value"""
    if value is None or pd.isna(value):
        return "M"
    return f"{value:.0f}"


def arrow(ax: Axes, x: float, y: float, drct: float):
    """Draw a arrow."""
    angle_deg = 90 - drct + 180
    ax.annotate(
        "→",
        xy=(x, y),
        ha="center",
        va="center",
        fontsize=16,
        rotation=angle_deg,
        color="black",
    )


def plotter(ctx: dict):
    """Go"""
    station = ctx["zstation"]
    plot_units = ctx["units"]
    year = ctx["year"]
    month = ctx["month"]
    sts = date(year, month, 1)
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper("""
                SELECT extract(year from day) as year,
                to_char(day, 'mmdd') as sday,
                day, avg_sknt as sknt, vector_avg_drct as drct,
                coalesce(max_gust, 0) as gust
                from summary s WHERE iemid = :iemid and
                extract(month from day) = :month and avg_sknt is not null
                ORDER by day ASC
        """),
            conn,
            params={"iemid": ctx["_nt"].sts[station]["iemid"], "month": month},
            parse_dates=["day"],
        )
    title = f"{ctx['_sname']}\n{sts:%b %Y} Daily Wind Speed and Direction"
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))

    xlabels = []
    xticks = []
    if not df.empty:
        # Convert speed to desired units
        df["speed"] = convert_value(df["sknt"], "knot", XREF_UNITS[plot_units])
        df["gust"] = convert_value(df["gust"], "knot", XREF_UNITS[plot_units])
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
            f"Smoothed Speed Climatology ({df['year'].min():.0f}-"
            f"{df['year'].max():.0f})"
        )
        # Get this year's data
        df = df[df["year"] == year]
        if not df.empty:
            ax.text(
                0,
                -0.02,
                "Day\nSpeed\nGust",
                ha="right",
                va="top",
                fontsize=8,
                transform=ax.transAxes,
            )
            ax.bar(
                df["day"].dt.day.values,
                df["gust"].values,
                color="red",
                align="center",
                label="Max Gust",
            )
            ax.bar(
                df["day"].dt.day.values,
                df["speed"].values,
                color="green",
                align="center",
                label="Average Speed",
            )
            pos = max(df["speed"].min() / 2.0, 0.5)
            # Leave 15% room at the top
            apos = max(df["speed"].max() * 1.075, df["gust"].max() * 1.075)
            for _, row in df.iterrows():
                x = row["day"].day
                xticks.append(x)
                xlabels.append(
                    "\n".join(
                        [str(x), pprint(row["speed"]), pprint(row["gust"])]
                    )
                )
                if pd.notna(row["drct"]):
                    arrow(ax, x, apos, row["drct"])
                if pd.notna(row["drct"]):
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
            ax.set_ylim(0, apos * 1.05)
            ax.plot(
                climo["day_of_month"],
                climo["speed"],
                "k-",
                lw=2,
                label=label,
            )
            ax.legend(loc=(0.0, -0.2), ncol=3)
        ax.grid(True, axis="y", zorder=11)
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
    if xlabels:
        ax.set_xticks(xticks)
        ax.set_xticklabels(xlabels, ha="center", fontsize=8)

    ax.set_ylabel(f"Wind Speed [{PDICT[plot_units]}]")

    return fig, df
