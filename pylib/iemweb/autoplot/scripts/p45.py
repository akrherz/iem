"""
Computes the frequency of having a day within
a month with an overcast sky reported at a given time of the day.  There
are a number of caveats to this plot as sensors and observing techniques
have changed over the years!  The algorithm specifically looks for the
OVC condition to be reported in the METAR observation.
"""

import calendar
from datetime import date, datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 86400, "data": True}
    today = date.today()
    desc["arguments"] = [
        dict(
            type="zstation",
            name="zstation",
            default="DSM",
            label="Select Station:",
            network="IA_ASOS",
        ),
        dict(
            type="hour", name="hour", label="Select Hour of Day:", default=12
        ),
        dict(
            type="year",
            name="year",
            label="Select Year to Compare by Month:",
            default=today.year,
        ),
        dict(
            type="month",
            name="month",
            label="Select Month to Compare by Year:",
            default=today.month,
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["zstation"]
    hour = ctx["hour"]
    year = ctx["year"]
    month = ctx["month"]
    with get_sqlalchemy_conn("asos") as conn:
        # This could use report_type=3, but its not all that slow and already
        # accounts for double-accounting.
        df = pd.read_sql(
            """
            WITH obs as (
                SELECT to_char(valid, 'YYYYmmdd') as yyyymmdd,
                SUM(case when (skyc1 = 'OVC' or skyc2 = 'OVC' or skyc3 = 'OVC'
                            or skyc4 = 'OVC') then 1 else 0 end)
                from alldata where station = %s and valid > '1951-01-01'
                and extract(hour from (valid at time zone %s) +
                    '10 minutes'::interval ) = %s
                GROUP by yyyymmdd)

            SELECT substr(o.yyyymmdd,1,4)::int as year,
            substr(o.yyyymmdd,5,2)::int as month,
            sum(case when o.sum >= 1 then 1 else 0 end) as hits, count(*)
            from obs o GROUP by year, month ORDER by year ASC, month ASC
        """,
            conn,
            params=(station, ctx["_nt"].sts[station]["tzname"], hour),
            index_col=None,
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["freq"] = df["hits"] / df["count"] * 100.0
    climo = df.groupby("month").sum()
    climo["freq"] = climo["hits"] / climo["count"] * 100.0

    title = (
        f"({df['year'].min():.0f}-{datetime.now().year}) "
        f"{ctx['_sname']}\n"
        f"Frequency of {datetime(2000, 1, 1, hour, 0):%I %p} "
        "Cloud Observation of Overcast"
    )
    fig = figure(apctx=ctx, title=title)
    ax = fig.subplots(2, 1)
    ax[0].bar(
        climo.index.values - 0.2,
        climo["freq"].values,
        fc="red",
        ec="red",
        width=0.4,
        label="Climatology",
        align="center",
    )
    for i, row in climo.iterrows():
        ax[0].text(
            i - 0.2, row["freq"] + 1, "%.0f" % (row["freq"],), ha="center"
        )

    thisyear = df[df["year"] == year]
    if not thisyear.empty:
        ax[0].bar(
            thisyear["month"].values + 0.2,
            thisyear["freq"].values,
            fc="blue",
            ec="blue",
            width=0.4,
            label=str(year),
            align="center",
        )
    for _, row in thisyear.iterrows():
        ax[0].text(
            row["month"] + 0.2,
            row["freq"] + 1,
            "%.0f" % (row["freq"],),
            ha="center",
        )
    ax[0].set_ylim(0, 100)
    ax[0].set_xlim(0.5, 12.5)
    ax[0].legend(ncol=2)
    ax[0].set_yticks([0, 10, 25, 50, 75, 90, 100])
    ax[0].set_xticks(range(1, 13))
    ax[0].grid(True)
    ax[0].set_xticklabels(calendar.month_abbr[1:])
    ax[0].set_ylabel("Frequency [%]")

    # Plot second one now
    obs = df[df["month"] == month]
    if not obs.empty:
        ax[1].bar(
            obs["year"].values, obs["freq"].values, fc="tan", ec="orange"
        )
        ax[1].set_ylim(0, 100)
        ax[1].grid(True)
        ax[1].set_yticks([0, 10, 25, 50, 75, 90, 100])
        ax[1].axhline(obs["freq"].mean())
        ax[1].set_ylabel(f"{calendar.month_abbr[month]} Frequency [%]")
        ax[1].set_xlim(obs["year"].min() - 2, obs["year"].max() + 2)
    return fig, df
