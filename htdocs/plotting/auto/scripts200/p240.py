"""
This autoplot combines growing degree day observations along with a near
term forecast from the deterministic GFS and NWS NDFD models.

<p>The primary source of observations for this plot is from the NWS COOP
network, but most of those observations are approximately 7 AM to 7 AM totals
whereas the forecast data is approximately a calendar date.  For sites that
report morning data, the observations are backed up one day to better align
with the forecast.  This then creates a problem when running the app in the
late afternoon/evening when the first forecast day is tomorrow and there
is no observation for today yet. This is generally a thorny issue and
why we can't have nice things.

<p>This app uses <a href="/plotting/auto/?q=9">Autoplot #9</a> to generate the
GDD Climatology.
"""
from datetime import date, timedelta

import requests
import pandas as pd
import matplotlib.dates as mdates
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        {
            "type": "station",
            "name": "station",
            "default": "IATDSM",
            "label": "Select Station:",
            "network": "IACLIMATE",
        },
        {
            "type": "date",
            "default": f"{date.today() - timedelta(days=7):%Y/%m/%d}",
            "name": "sdate",
            "label": "Select start date to accumulate GDDs",
        },
    ]
    return desc


def get_obsdf(ctx):
    """Figure out our observations."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            text(
                """
                SELECT day, gddxx(50, 86, high, low) as gdd, temp_hour
                from alldata
                WHERE station = :station and day >= :sts ORDER by day ASC
            """
            ),
            conn,
            index_col="day",
            parse_dates=["day"],
            params={
                "station": ctx["station"],
                "sts": ctx["sdate"],
            },
        )
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())

    df = get_obsdf(ctx)
    # Account for morning obs
    is_morning = False
    if not df.empty:
        cnt = len(df[(df["temp_hour"] > 1) & (df["temp_hour"] < 12)].index)
        if cnt / len(df.index) > 0.5:
            is_morning = True
    req = requests.get(
        "http://mesonet.agron.iastate.edu/json/climodat_dd.py?"
        f"station={ctx['station']}&gddbase=50&gddceil=86&",
        timeout=60,
    )
    data = req.json()
    gfsdf = pd.DataFrame(data["gfs"])
    gfsdf["date"] = pd.to_datetime(gfsdf["date"])
    if is_morning:
        if not df.empty and df.index.values[-1] == gfsdf["date"].values[0]:
            df["gdd"] = df["gdd"].shift(-1)
        else:
            is_morning = False
    gfsdf = gfsdf.set_index("date")
    nwsdf = pd.DataFrame(data["ndfd"])
    nwsdf["date"] = pd.to_datetime(nwsdf["date"])
    nwsdf = nwsdf.set_index("date")
    df = df.join(nwsdf, how="outer", rsuffix="ndfd")
    df = df.join(gfsdf, how="outer", rsuffix="gfs")
    if df.empty:
        raise NoDataFound("No data found!")
    df["sday"] = df.index.strftime("%m%d")

    v1 = df.index.strftime("%m%d").values[0]
    v2 = df.index.strftime("%m%d").values[-1]
    # Climo
    url = (
        "http://iem.local/plotting/auto/plot/9/network:"
        f"{ctx['station'][:2]}CLIMATE::station:{ctx['station']}::year:2023::"
        f"var:gdd::base:50::ceiling:86::w:ytd::sday:{v1}::eday:{v2}."
        "csv"
    )
    try:
        climodf = pd.read_csv(url, dtype={"sday": str}).set_index("sday")
    except Exception as exp:
        raise NoDataFound("Failed to load climatology, aborting.") from exp
    df = df.merge(climodf, left_on="sday", right_index=True)

    xaxis = df.index.values

    fig = figure(
        title=(
            f"({df.index[0]:%-d %b %Y}-{df.index[-1]:%-d %b %Y}) "
            f"{ctx['_sname']}:: Growing Degree Days (50/86)"
        ),
        subtitle=(
            "Based on Observations, GFS Operational Forecast, "
            "NWS NDFD Forecast"
        ),
    )
    ax = fig.add_axes([0.06, 0.1, 0.85, 0.75])
    ax.bar(xaxis, df["gdd"].values, color="g", label="Observed")
    ax.bar(xaxis, df["gddndfd"].values, color="r", label="NWS NDFD", width=0.4)
    ax.bar(
        xaxis,
        df["gddgfs"].values,
        color="b",
        label="GFS",
        width=0.4,
        align="edge",
    )
    avgval = df["mean"] - df["mean"].shift(1)
    avgval.iloc[0] = df["mean"].iloc[0]
    ax.bar(
        xaxis,
        [0.1] * len(df.index),
        bottom=(avgval - 0.1),
        color="k",
        label="Climo",
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    ax.grid(True)
    ax.set_ylabel("Daily GDDs (bars)")
    ax.legend(loc=(0, 1.01), ncol=5)

    ax2 = ax.twinx()
    ax2.plot(
        xaxis,
        df["gddgfs"].combine_first(df["gdd"]).cumsum(),
        color="white",
        zorder=4,
        lw=4,
    )
    ax2.plot(
        xaxis,
        df["gddgfs"].combine_first(df["gdd"]).cumsum(),
        color="b",
        zorder=5,
        lw=2,
    )

    ax2.plot(
        xaxis,
        df["gddndfd"].combine_first(df["gdd"]).cumsum(),
        color="white",
        zorder=4,
        lw=4,
    )
    ax2.plot(
        xaxis,
        df["gddndfd"].combine_first(df["gdd"]).cumsum(),
        color="r",
        zorder=5,
        lw=2,
    )
    ax2.plot(xaxis, df["gdd"].cumsum(), label="Obs", color="g", zorder=5)
    ax2.plot(xaxis, df["mean"].values, color="k")
    ax2.set_ylabel("Accumulated GDDs (lines)")
    if is_morning:
        ax.set_xlabel("* Observations shifted one day due to morning reports")
    return fig, df


if __name__ == "__main__":
    plotter({"station": "IA0203"})
