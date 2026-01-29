"""
This plot displays some metrics about the start
date and duration of the spring or fall season.
The definition of the season
being the period between the coldest 91 day stretch and subsequent
warmest 91 day stretch.  91 days being approximately 1/4 of the year,
assuming the four seasons are to be equal duration.  Of course, this is
arbitrary, but interesting to look at!
"""

from datetime import date, timedelta

import matplotlib.dates as mdates
import pandas as pd
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from scipy import stats

from iemweb.autoplot import ARG_STATION

PDICT = {"spring": "Spring Season", "fall": "Fall Season"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    desc["arguments"] = [
        ARG_STATION,
        dict(
            type="select",
            name="season",
            default="spring",
            options=PDICT,
            label="Which Season to Highlight:",
        ),
        dict(
            type="year",
            name="year",
            default=(date.today().year - 2),
            label="Select Start Year (3 years plotted) for Top Panel:",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    station = ctx["station"]
    year = ctx["year"]
    season = ctx["season"]

    with get_sqlalchemy_conn("coop") as conn:
        # Have to do a redundant query to get the running values
        obs = pd.read_sql(
            sql_helper("""
        WITH trail as (
            SELECT day, year,
            avg((high+low)/2.) OVER (ORDER by day ASC ROWS 91 PRECEDING)
            as avgt from alldata WHERE station = :station)

        SELECT day, avgt from trail WHERE year between :y1 and :y2
        ORDER by day ASC
        """),
            conn,
            params={"station": station, "y1": year, "y2": year + 2},
            index_col="day",
        )
    if obs.empty:
        raise NoDataFound("No Data Found.")
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        WITH trail as (
            SELECT day, year,
            avg((high+low)/2.) OVER (ORDER by day ASC ROWS 91 PRECEDING)
            as avgt from alldata WHERE station = :station),
        extremes as (
            SELECT day, year, avgt,
            rank() OVER (PARTITION by year ORDER by avgt ASC) as minrank,
            rank() OVER (PARTITION by year ORDER by avgt DESC) as maxrank
            from trail),
        yearmax as (
            SELECT year, min(day) as summer_end, min(avgt) as summer
            from extremes where maxrank = 1 GROUP by year),
        yearmin as (
            SELECT year, min(day) as winter_end, min(avgt) as winter
            from extremes where minrank = 1 GROUP by year)

        SELECT x.year, winter_end, winter, summer_end, summer,
        extract(doy from winter_end)::int as winter_end_doy,
        extract(doy from summer_end)::int as summer_end_doy
        from yearmax x JOIN yearmin n on (x.year = n.year) ORDER by x.year ASC
        """),
            conn,
            params={"station": station},
            index_col="year",
        )
    # Throw out spring of the first year
    for col in ["winter", "winter_end_doy", "winter_end"]:
        df.at[df.index.min(), col] = None

    # Need to cull current year
    if date.today().month < 8:
        for col in ["summer", "summer_end_doy", "summer_end"]:
            df.at[date.today().year, col] = None
    if date.today().month < 2:
        for col in ["winter", "winter_end_doy", "winter_end"]:
            df.at[date.today().year, col] = None
    df["spring_length"] = df["summer_end_doy"] - 91 - df["winter_end_doy"]
    # fall is a bit tricker
    df["fall_length"] = None
    df.loc[df.index[:-1], "fall_length"] = (
        (df["winter_end_doy"].values[1:] + 365)
        - 91
        - df["summer_end_doy"].values[:-1]
    )

    df["fall_length"] = pd.to_numeric(df["fall_length"])
    fig = figure(apctx=ctx)
    ax = fig.subplots(3, 1)

    ax[0].plot(obs.index.values, obs["avgt"].values)
    ax[0].set_ylim(obs["avgt"].min() - 8, obs["avgt"].max() + 8)
    ab = ctx["_nt"].sts[station]["archive_begin"]
    if ab is None:
        raise NoDataFound("Unknown station metadata.")
    ax[0].set_title(
        f"{ab.year}-{year + 3} {ctx['_sname']}\n91 Day Average Temperatures"
    )
    ax[0].set_ylabel("Trailing 91 Day Avg T °F")
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax[0].grid(True)

    # Label the maxes and mins
    for yr in range(year, year + 3):
        if yr not in df.index:
            continue
        dt = df.at[yr, "winter_end"]
        val = df.at[yr, "winter"]
        if pd.notna(dt):
            ax[0].text(
                dt,
                val - 1,
                f"{dt:%-d %b} {val:.1f}°F",
                ha="center",
                va="top",
                bbox=dict(color="white", boxstyle="square,pad=0"),
            )
        dt = df.at[yr, "summer_end"]
        val = df.at[yr, "summer"]
        if pd.notna(dt):
            ax[0].text(
                dt,
                val + 1,
                f"{dt:%-d %b} {val:.1f}°F",
                ha="center",
                va="bottom",
                bbox=dict(color="white", boxstyle="square,pad=0"),
            )

    df2 = df.dropna()
    p2col = "winter_end_doy" if season == "spring" else "summer_end_doy"
    slp, intercept, r, _, _ = stats.linregress(
        df2.index.values, df2[p2col].values
    )
    ax[1].scatter(df.index.values, df[p2col].values)
    ax[1].grid(True)
    # Do labelling
    yticks = []
    yticklabels = []
    for doy in range(int(df[p2col].min()), int(df[p2col].max())):
        dt = date(2000, 1, 1) + timedelta(days=doy - 1)
        if dt.day in [1, 15]:
            yticks.append(doy)
            yticklabels.append(dt.strftime("%-d %b"))
    ax[1].set_yticks(yticks)
    ax[1].set_yticklabels(yticklabels)
    lbl = (
        "Date of Minimum (Spring Start)"
        if season == "spring"
        else "Date of Maximum (Fall Start)"
    )
    ax[1].set_ylabel(lbl)
    ax[1].set_xlim(df.index.min() - 1, df.index.max() + 1)
    avgv = df[p2col].mean()
    ax[1].axhline(avgv, color="r")
    ax[1].plot(df.index.values, intercept + (df.index.values * slp))
    d = (date(2000, 1, 1) + timedelta(days=int(avgv))).strftime("%-d %b")
    ax[1].text(
        0.02,
        0.02,
        r"$\frac{\Delta days}{decade} = %.2f,R^2=%.2f, avg = %s$"
        % (slp * 10.0, r**2, d),
        va="bottom",
        transform=ax[1].transAxes,
    )
    ax[1].set_ylim(bottom=ax[1].get_ylim()[0] - 10)

    p3col = "spring_length" if season == "spring" else "fall_length"
    slp, intercept, r, _, _ = stats.linregress(df2.index.values, df2[p3col])
    ax[2].scatter(df.index.values, df[p3col])
    ax[2].set_xlim(df.index.min() - 1, df.index.max() + 1)
    ax[2].set_ylabel("Length of '%s' [days]" % (season.capitalize(),))
    ax[2].grid(True)
    avgv = df[p3col].mean()
    ax[2].axhline(avgv, color="r")
    ax[2].plot(df.index.values, intercept + (df.index.values * slp))
    ax[2].text(
        0.02,
        0.02,
        r"$\frac{\Delta days}{decade} = %.2f,R^2=%.2f, avg = %.1fd$"
        % (slp * 10.0, r**2, avgv),
        va="bottom",
        transform=ax[2].transAxes,
    )
    ax[2].set_ylim(bottom=ax[2].get_ylim()[0] - 15)

    return fig, df
