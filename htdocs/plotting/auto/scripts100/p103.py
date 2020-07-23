"""Steps up and down"""
import calendar

import numpy as np
from pandas.io.sql import read_sql
from pyiem import network
from pyiem.plot.use_agg import plt
from pyiem.util import get_autoplot_context, get_dbconn
from pyiem.exceptions import NoDataFound

PDICT = {"spring": "1 January - 31 December", "fall": "1 July - 30 June"}


def get_description():
    """ Return a dict describing how to call this plotter """
    desc = dict()
    desc["data"] = True
    desc[
        "description"
    ] = """This plot analyzes the number of steps down in
    low temperature during the fall season and the number of steps up in
    high temperature during the spring season.  These steps are simply having
    a newer colder low or warmer high for the season to date period.
    """
    desc["arguments"] = [
        dict(
            type="station",
            name="station",
            default="IATDSM",
            label="Select Station",
            network="IACLIMATE",
        ),
        dict(
            type="select",
            name="season",
            options=PDICT,
            label="Select which half of year",
            default="fall",
        ),
    ]
    return desc


def plotter(fdict):
    """ Go """
    pgconn = get_dbconn("coop")

    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    season = ctx["season"]
    table = "alldata_%s" % (station[:2],)
    nt = network.Table("%sCLIMATE" % (station[:2],))

    year = (
        "case when month > 6 then year + 1 else year end"
        if season == "fall"
        else "year"
    )
    df = read_sql(
        f"""
    WITH obs as (
        SELECT day, month, high, low, {year} as season
        from {table} WHERE station = %s),
    data as (
        SELECT season, day,
        max(high) OVER (PARTITION by season ORDER by day ASC
                        ROWS BETWEEN 366 PRECEDING and CURRENT ROW) as mh,
        min(low) OVER (PARTITION by season ORDER by day ASC
                       ROWS BETWEEN 366 PRECEDING and CURRENT ROW) as ml
        from obs),
    lows as (
        SELECT season, day, ml as level,
        rank() OVER (PARTITION by season, ml ORDER by day ASC) from data),
    highs as (
        SELECT season, day, mh as level,
        rank() OVER (PARTITION by season, mh ORDER by day ASC) from data)

    (SELECT season as year, day, extract(doy from day) as doy,
     level, 'fall' as typ from lows WHERE rank = 1) UNION
    (SELECT season as year, day, extract(doy from day) as doy,
     level, 'spring' as typ from highs WHERE rank = 1)
    """,
        pgconn,
        params=[station],
    )
    if df.empty:
        raise NoDataFound("No Data Found.")
    df2 = df[df["typ"] == season]
    (fig, ax) = plt.subplots(3, 1, figsize=(7, 10))
    dyear = df2.groupby(["year"]).count()
    ax[0].bar(dyear.index, dyear["level"], facecolor="tan", edgecolor="tan")
    ax[0].axhline(dyear["level"].mean(), lw=2)
    ax[0].set_ylabel("Yearly Events Avg: %.1f" % (dyear["level"].mean(),))
    ax[0].set_xlim(dyear.index.min() - 1, dyear.index.max() + 1)
    title = "%s Steps %s" % (
        PDICT[season],
        "Down" if season == "fall" else "Up",
    )
    ax[0].set_title(
        "%s [%s]\n%s in Temperature"
        % (nt.sts[station]["name"], station, title)
    )
    ax[0].grid(True)

    ax[1].hist(
        np.array(df2["level"], "f"),
        bins=np.arange(df2["level"].min(), df2["level"].max() + 1, 2),
        density=True,
        facecolor="tan",
    )
    ax[1].set_ylabel("Probability Density")
    ax[1].axvline(32, lw=2)
    ax[1].grid(True)
    ax[1].set_xlabel(r"Temperature $^\circ$F, 32 degrees highlighted")

    ax[2].hist(
        np.array(df2["doy"], "f"),
        bins=np.arange(df2["doy"].min(), df2["doy"].max() + 1, 3),
        density=True,
        facecolor="tan",
    )
    ax[2].set_xticks((1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    ax[2].set_xticklabels(calendar.month_abbr[1:])
    ax[2].set_xlim(df2["doy"].min() - 3, df2["doy"].max() + 3)

    ax[2].set_ylabel("Probability Density")
    ax[2].grid(True)
    ax[2].set_xlabel("Day of Year, 3 Day Bins")

    return fig, df


if __name__ == "__main__":
    plotter(dict())
