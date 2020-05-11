"""Precip sums"""
import calendar

import psycopg2.extras
import pandas as pd
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
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
    """ Go """
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    threshold = float(ctx["threshold"])

    table = "alldata_%s" % (station[:2],)

    cursor.execute(
        """
         WITH monthly as (
         SELECT year, month, max(precip), sum(precip) from """
        + table
        + """
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

    (fig, ax) = plt.subplots(1, 1)

    ax.bar(df.index, df.freq, align="center")
    for i, row in df.iterrows():
        ax.text(i, row["freq"] + 2, "%.1f" % (row["freq"],), ha="center")
    ax.set_title(
        (
            "[%s] %s\nFreq of One Day Having %.0f%% of That Month's "
            "Precip Total"
        )
        % (station, ctx["_nt"].sts[station]["name"], threshold)
    )
    ax.grid(True)
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage of Years")
    ax.set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax.set_xticklabels(calendar.month_abbr[1:])
    ax.set_xticks(range(1, 13))

    return fig, df


if __name__ == "__main__":
    plotter(dict())
