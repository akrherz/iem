"""
This plot presents a time series of
observations.  Please note the colors and axes labels used to denote
which variable is which in the combination plots.
"""

from datetime import date, timedelta
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib import ticker
from matplotlib.artist import setp
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from metpy.units import units
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import utc

PDICT = {
    "default": "Temperatures | Winds | Clouds + Vis",
    "two": "Temperatures | Winds | Pressure",
}


def date_ticker(ax: Axes, mytz):
    """Timestamp formatter"""
    (xmin, xmax) = ax.get_xlim()
    if xmin < 1:
        return
    xmin = mdates.num2date(xmin)
    xmax = mdates.num2date(xmax)
    xmin = xmin.replace(minute=0)
    xmax = (xmax + timedelta(minutes=59)).replace(minute=0)
    now = xmin
    xticks = []
    xticklabels = []
    while now <= xmax:
        lts = now.astimezone(mytz)
        if lts.hour % 6 == 0:
            fmt = "%-I %p\n%-d %b" if lts.hour == 0 else "%-I %p"
            xticks.append(now)
            xticklabels.append(lts.strftime(fmt))
        if len(xticks) > 100:
            break
        now += timedelta(hours=1)

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 360}
    desc["defaults"] = {"_r": "88"}
    d3 = date.today() - timedelta(days=2)
    desc["arguments"] = [
        dict(
            type="sid",
            label="Select IEM Tracked Station",
            name="station",
            default="AMW",
            network="IA_ASOS",
        ),
        dict(
            type="date",
            default=d3.strftime("%Y/%m/%d"),
            name="sdate",
            label="Start Date of Plot: (optional)",
            optional=True,
        ),
        dict(
            type="select",
            options=PDICT,
            default="default",
            label="Plot Type",
            name="p",
        ),
    ]
    return desc


def get_data(network: str, station, tzname, sdate) -> pd.DataFrame:
    """retrieve the data frame we want"""
    if sdate is None:
        with get_sqlalchemy_conn("iem") as conn:
            df = pd.read_sql(
                sql_helper("""
                SELECT tmpf, dwpf, sknt, gust, drct, skyc1, skyc2, skyc3,
                skyc4, skyl1, skyl2, skyl3, skyl4, vsby, alti,
                valid at time zone 'UTC' as utc_valid
                from current_log c JOIN stations t ON (t.iemid = c.iemid)
                WHERE t.network = :network and t.id = :station and
                valid > now() - '4 days'::interval ORDER by valid ASC
            """),
                conn,
                params={"network": network, "station": station},
                index_col="utc_valid",
            )
        return df

    sts = utc(2018)
    sts = sts.astimezone(ZoneInfo(tzname))
    sts = sts.replace(
        year=sdate.year, month=sdate.month, day=sdate.day, hour=0, minute=0
    )
    ets = sts + timedelta(hours=72)
    if network.endswith("ASOS"):
        with get_sqlalchemy_conn("asos") as conn:
            df = pd.read_sql(
                sql_helper("""
                SELECT tmpf, dwpf, sknt, gust, drct, skyc1, skyc2, skyc3,
                skyc4, skyl1, skyl2, skyl3, skyl4, vsby, alti,
                valid at time zone 'UTC' as utc_valid
                from alldata WHERE station = :station and
                valid >= :sts and valid < :ets
                ORDER by valid ASC
            """),
                conn,
                params={"station": station, "sts": sts, "ets": ets},
                index_col="utc_valid",
            )
        return df
    raise NoDataFound("No data was found for this site.")


def ceilingfunc(row: dict) -> float:
    """Our logic to compute a ceiling"""
    c = [row["skyc1"], row["skyc2"], row["skyc3"], row["skyc4"]]
    if "OVC" not in c:
        return np.nan
    pos = c.index("OVC")
    larr = [row["skyl1"], row["skyl2"], row["skyl3"], row["skyl4"]]
    if pd.isnull(larr[pos]):
        return None
    return larr[pos] / 1000.0


def plot_df(ctx: dict, df: pd.DataFrame, tzname: str) -> Figure:
    """Do some plotting."""
    df["time_delta"] = (
        df["utc_valid"] - df.shift(1)["utc_valid"]
    ).dt.total_seconds()
    df = df.set_index("utc_valid")

    df["ceiling"] = df.apply(ceilingfunc, axis=1)

    title = (
        f"{ctx['_sname']}\n"
        f"Recent Time Series {pd.to_datetime(df.index.values[0]):%Y %b %-d} - "
        f"{pd.to_datetime(df.index.values[-1]):%Y %b %-d}"
    )
    fig = figure(apctx=ctx, title=title)
    xalign = 0.1
    xwidth = 0.8
    ax = fig.add_axes((xalign, 0.7, xwidth, 0.2))

    xmin = df.index.min()
    xmax = df.index.max()
    # ____________PLOT 1___________________________
    df2 = df[df["tmpf"].notnull()]
    ax.plot(
        df2.index.values,
        df2["tmpf"],
        lw=2,
        label="Air Temp",
        color="#db6065",
        zorder=2,
    )
    df2 = df[df["dwpf"].notnull()]
    ax.plot(
        df2.index.values,
        df2["dwpf"],
        lw=2,
        label="Dew Point",
        color="#346633",
        zorder=3,
    )
    ax.grid(True)
    ax.text(
        -0.1,
        0,
        "Temperature [F]",
        rotation=90,
        transform=ax.transAxes,
        verticalalignment="bottom",
    )
    if not df2.empty:
        ax.set_ylim(bottom=df["dwpf"].min() - 3)
    setp(ax.get_xticklabels(), visible=True)
    date_ticker(ax, ZoneInfo(tzname))
    ax.set_xlim(xmin, xmax)
    ax.legend(loc="best", ncol=2)

    # _____________PLOT 2____________________________
    ax = fig.add_axes((xalign, 0.4, xwidth, 0.25))

    ax2 = ax.twinx()
    df2 = df[df["gust"].notnull()]
    if not df2.empty:
        ax2.bar(
            df2.index.values,
            (df2["gust"].values * units("knot")).to(units("mile / hour")).m,
            width=df2["time_delta"].values / 86400.0,
            color="#9898ff",
            zorder=2,
        )
    df2 = df[df["sknt"].notnull()]
    if not df2.empty:
        ax2.bar(
            df2.index.values,
            (df2["sknt"].values * units("knot")).to(units("mile / hour")).m,
            width=df2["time_delta"].values / 86400.0,
            color="#373698",
            zorder=3,
        )
    ax2.set_ylim(bottom=0)
    ax.set_yticks(range(0, 361, 45))
    ax.set_yticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax.set_ylabel("Wind Direction")
    ax2.set_ylabel("Wind Speed [mph]")
    ax.set_ylim(0, 360.1)
    date_ticker(ax, ZoneInfo(tzname))
    ax.scatter(
        df2.index.values,
        df2["drct"],
        facecolor="None",
        edgecolor="#b8bc74",
        zorder=4,
    )
    ax.set_zorder(ax2.get_zorder() + 1)
    ax.patch.set_visible(False)
    ax.set_xlim(xmin, xmax)
    ax2.yaxis.set_major_locator(ticker.LinearLocator(9))
    ax.grid(True)

    # _________ PLOT 3 ____
    ax = fig.add_axes((xalign, 0.1, xwidth, 0.25))
    if ctx["p"] == "default":
        ax2 = ax.twinx()
        ax2.scatter(
            df.index.values,
            df["ceiling"],
            label="Visibility",
            marker="o",
            s=40,
            color="g",
        )
        ax2.set_ylabel("Overcast Ceiling [k ft]", color="g")
        ax2.set_ylim(bottom=0)
        ax.scatter(
            df.index.values,
            df["vsby"],
            label="Visibility",
            marker="*",
            s=40,
            color="b",
        )
        ax.set_ylabel("Visibility [miles]")
        ax.set_ylim(0, 14)
    elif ctx["p"] == "two":
        df2 = df[(df["alti"] > 20.0) & (df["alti"] < 40.0)]
        ax.grid(True)
        if not df2.empty:
            vals = (df2["alti"].values * units("inch_Hg")).to(units("hPa")).m
            ax.fill_between(df2.index.values, 0, vals, color="#a16334")
            ax.set_ylim(bottom=(vals.min() - 1), top=vals.max() + 1)
            ax.set_ylabel("Pressure [mb]")

    ax.set_xlim(xmin, xmax)
    date_ticker(ax, ZoneInfo(tzname))
    ax.set_xlabel(f"Plot Time Zone: {tzname}")
    ax.yaxis.set_major_locator(ticker.LinearLocator(9))
    ax2.yaxis.set_major_locator(ticker.LinearLocator(9))
    ax.grid(True)
    return fig


def plotter(ctx: dict):
    """This autoplot gets hit a lot, so we attempt to always generate."""
    station = ctx["station"]
    sdate = ctx.get("sdate")

    fig = None
    df = pd.DataFrame()
    if ctx["network"].find("COOP") == -1:
        tzname = ctx["_nt"].sts[station]["tzname"] or "America/Chicago"
        df = get_data(ctx["network"], station, tzname, sdate).reset_index()
        if not df.empty:
            fig = plot_df(ctx, df, tzname)
    if fig is None:
        fig = figure(
            title=f"{ctx['_sname']} Recent Time Series",
            apctx=ctx,
        )
        fig.text(
            0.5,
            0.5,
            "No recent data available for this station.",
            ha="center",
            va="center",
        )

    return fig, df
