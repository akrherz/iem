"""
This plot presents the largest drop in low
temperature during a period between 1 July and 30 June of the next year,
but not including the July data of that year. The drop compares the lowest
low previous to the date with the low for that date.  For example,
if your coldest low to date was 40, you would not expect to see a
low temperature of 20 the next night without first setting colder
daily low temperatures. See also
<a class="alert-link" href="/plotting/auto/?q=103">autoplot 103</a>
for more details.
"""

from calendar import month_abbr
from datetime import date

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context


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
            type="year",
            name="year",
            default=date.today().year,
            label="Year to Highlight",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    year = ctx["year"]
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
        with obs as (
        select day, (case when month < 7 then year - 1 else year end)
            as myyear,
        low, month from alldata where station = %s
        ), obs2 as (
            select day, myyear, low, month,
            low - min(low) OVER
            (PARTITION by myyear ORDER by day ASC ROWS between 400 PRECEDING
            and 1 PRECEDING) as drop from obs
        ), agg as (
            select day, myyear, low, drop,
            rank() OVER (PARTITION by myyear ORDER by drop ASC) as rank
            from obs2 WHERE month != 7
        )
        select myyear as year, day, low, drop as largest_change
        from agg where rank = 1
        """,
            conn,
            params=(station,),
            index_col="year",
            parse_dates="day",
        )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df["largest_change"] = df["largest_change"] * -1
    title = (
        f"{ctx['_sname']}\n"
        "Max 1 Aug till 30 Jun Low Temp Drop Exceeding "
        "Previous Min Low for Season"
    )

    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes([0.1, 0.1, 0.4, 0.75])
    df2 = df.groupby("year").max()
    ax.bar(
        df2.index.values,
        df2["largest_change"],
        fc="b",
        ec="b",
        zorder=1,
    )
    if year in df.index:
        ax.bar(
            year,
            df.at[year, "largest_change"],
            fc="red",
            ec="red",
            zorder=2,
        )
        ax.set_xlabel(f"{year} value is {df.at[year, 'largest_change']}")
    mv = df["largest_change"].mean()
    ax.axhline(mv, lw=2, color="k")
    ax.grid(True)
    ax.set_ylabel(r"Largest Low Temp Drop $^\circ$F, " f"Avg: {mv:.1f}")
    ax.set_xlim(df.index.values.min() - 1, df.index.values.max() + 1)

    ax = fig.add_axes([0.58, 0.12, 0.4, 0.32])
    ax.scatter(
        [int(x) for x in df["day"].dt.strftime("%j").values],
        df["largest_change"].values,
    )
    ax.set_xticks([1, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
    ax.set_xticklabels(month_abbr[1:], rotation=45)
    ax.set_ylabel(r"Drop $^\circ$F")
    ax.set_xlabel("On Date")
    ax.grid(True)

    ax = fig.add_axes([0.58, 0.56, 0.4, 0.32])
    ax.scatter(
        df["low"].values,
        df["largest_change"].values,
    )
    ax.set_ylabel(r"Drop $^\circ$F")
    ax.set_xlabel(r"At Temperature $^\circ$F")
    ax.grid(True)

    return fig, df
