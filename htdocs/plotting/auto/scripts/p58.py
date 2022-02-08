"""Precip sums"""
import calendar

import psycopg2.extras
import pandas as pd
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """Displays the number of times that a single day's
    precipitation was greater than some portion of the monthly total. The
    default settings provide the frequency of getting half of the month's
    precipitation within one 24 hour period."""
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            network="IACLIMATE",
            label="Select Station:",
        ),
        dict(
            type="text",
            name="threshold",
            default=50,
            label="Percentage of Monthly Precipitation on One Day",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = float(ctx["threshold"])

    cursor.execute(
        f"""
         WITH monthly as (
         SELECT year, month, max(precip), sum(precip)
         from alldata_{station[:2]}
         WHERE station = %s and precip is not null GROUP by year, month)

         SELECT month, sum(case when max > (sum * %s) then 1 else 0 end),
         count(*) from monthly GROUP by month ORDER by month ASC
         """,
        (station, threshold / 100.0),
    )
    df = pd.DataFrame(
        dict(
            freq=pd.Series(),
            events=pd.Series(),
            month=pd.Series(calendar.month_abbr[1:], index=range(1, 13)),
        ),
        index=pd.Series(range(1, 13), name="mo"),
    )
    for row in cursor:
        df.at[row[0], "events"] = row[1]
        df.at[row[0], "freq"] = row[1] / float(row[2]) * 100.0

    title = (
        f"[{station}] {ctx['_nt'].sts[station]['name']}\n"
        f"Freq of One Day Having {threshold:.0f}% of That Month's Precip Total"
    )
    (fig, ax) = figure_axes(apctx=ctx, title=title)

    ax.bar(df.index, df.freq, align="center")
    for i, row in df.iterrows():
        ax.text(i, row["freq"] + 2, f"{row['freq']:.1f}", ha="center")
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage of Years")
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(calendar.month_abbr[1:])

    return fig, df


if __name__ == "__main__":
    plotter({})
