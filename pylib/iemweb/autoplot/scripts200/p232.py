"""
This app plots ASOS/METAR data during a period of your choice and overlays
NWS Watch, Warning, and Advisory data.  The choice of NWS Headline type
will limit which potential headlines events are overlaid on the chart.
"""

import datetime
from zoneinfo import ZoneInfo

# third party
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.exceptions import NoDataFound
from pyiem.nws.vtec import NWS_COLORS, get_ps_string
from pyiem.plot import figure
from pyiem.util import (
    get_autoplot_context,
    get_sqlalchemy_conn,
)
from sqlalchemy import text

PDICT = {
    "BZ": "Blizzard Warning",
    "WC": "Wind Chill Advisory/Warning",
    "HT": "Heat Advisory / Extreme Heat Warning",
}
DOMAIN = {
    "BZ": [
        "BZ.W",
    ],
    "WC": ["WC.W", "WC.Y", "WW.Y", "WS.W", "BZ.W"],
    "HT": ["EH.W", "HT.Y"],
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 600, "data": True}
    desc["defaults"] = {"_r": "t"}
    desc["arguments"] = [
        dict(
            type="select",
            name="mode",
            default="BZ",
            label="Customize plot for given NWS Headline:",
            options=PDICT,
        ),
        dict(
            type="zstation",
            default="MCW",
            network="IA_ASOS",
            name="station",
            label="Select station to plot:",
        ),
        dict(
            type="datetime",
            name="valid",
            default="2022/12/21 1200",
            label="Start time of plot (UTC):",
            min="2007/01/01 0000",
        ),
        dict(
            type="int",
            name="hours",
            default="72",
            label="Number of hours to plot observations for:",
        ),
    ]
    return desc


def plot(ax, obs, col):
    """Plot simple."""
    ax.scatter(obs.utc_valid, obs[col], marker="o", s=40, color="b", zorder=3)
    ax.set_ylabel(r"Feels Like Temperature [$^\circ$F]", color="b")


def plot_bz(ax, obs):
    """Do the magic with plotting for BZ."""
    ax.scatter(obs.utc_valid, obs.vsby, marker="o", s=40, color="b", zorder=2)
    ax.set_ylabel("Visibility [mile]", color="b")
    ax2 = ax.twinx()
    ax2.scatter(
        obs.utc_valid, obs.max_wind, marker="o", s=40, color="r", zorder=2
    )
    ax2.set_ylabel("Wind Speed/Gust [mph]", color="r")
    ax.set_ylim(0, 10.1)
    ax2.set_ylim(0, 80)

    ax.set_yticks(np.linspace(0, 10, 5))
    ax2.set_yticks(np.linspace(0, 80, 5))
    ax2.axhline(35, linestyle="-.", color="r")
    ax.axhline(0.25, linestyle="-.", color="b")

    hit = None
    row = None
    for j, row in obs.iterrows():
        if j == 0:
            continue
        if row["vsby"] <= 0.25 and row["max_wind"] >= 35:
            if hit is None:
                hit = j - 1
            continue
        if hit is None:
            continue
        secs = (row["utc_valid"] - obs.at[hit, "utc_valid"]).total_seconds()
        color = "#EEEEEE" if secs < (3 * 3600.0) else "lightblue"
        rect = Rectangle(
            (obs.at[hit, "utc_valid"], 0),
            datetime.timedelta(seconds=secs),
            60,
            fc=color,
            zorder=1,
            ec="None",
        )
        ax.add_patch(rect)
        hit = None
    if hit:
        secs = (row["utc_valid"] - obs.at[hit, "utc_valid"]).total_seconds()
        color = "#EEEEEE" if secs < (3 * 3600.0) else "lightblue"
        rect = Rectangle(
            (obs.at[hit, "utc_valid"], 0),
            datetime.timedelta(seconds=secs),
            60,
            fc=color,
            zorder=1,
            ec="None",
        )
        ax.add_patch(rect)


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx["valid"].replace(tzinfo=datetime.timezone.utc)
    station = ctx["station"]
    tzname = ctx["_nt"].sts[station]["tzname"]
    ets = sts + datetime.timedelta(hours=ctx["hours"])

    # Find WaWa
    with get_sqlalchemy_conn("postgis") as conn:
        wwa = pd.read_sql(
            text(
                """
            SELECT phenomena ||'.'|| significance as key,
            issue at time zone 'UTC' as utc_issue,
            expire at time zone 'UTC' as utc_expire, eventid
            from warnings where ugc = ANY(:ugcs) and issue < :ets
            and expire > :sts ORDER by issue ASC"""
            ),
            conn,
            params={
                "ugcs": [
                    ctx["_nt"].sts[station]["ugc_zone"],
                    ctx["_nt"].sts[station]["ugc_county"],
                ],
                "sts": sts,
                "ets": ets,
            },
            index_col=None,
        )
    if not wwa.empty:
        wwa["utc_issue"] = wwa["utc_issue"].dt.tz_localize(ZoneInfo("UTC"))
        wwa["utc_expire"] = wwa["utc_expire"].dt.tz_localize(ZoneInfo("UTC"))
        wwa = wwa[wwa["key"].isin(DOMAIN[ctx["mode"]])].reset_index()
    # Find Obs
    with get_sqlalchemy_conn("asos") as conn:
        obs = pd.read_sql(
            text(
                """
            SELECT valid at time zone 'UTC' as utc_valid, tmpf, sknt, gust,
            greatest(sknt, gust) * 1.15 as max_wind, feel,
            vsby from alldata where station = :station and
            valid >= :sts and valid <= :ets and report_type in (3, 4)
            ORDER by valid ASC"""
            ),
            conn,
            params={
                "station": station,
                "sts": sts,
                "ets": ets,
            },
            index_col=None,
        )
    if obs.empty:
        raise NoDataFound("No observations found for the site/time")

    title = f"{ctx['_sname']} :: Observations during NWS Headlines"
    subtitle = f"Plot customized for {PDICT[ctx['mode']]}."
    fig = figure(title=title, subtitle=subtitle, apctx=ctx)
    box1 = [0.1, 0.15, 0.82, 0.65]
    box2 = [0.1, 0.8, 0.82, 0.1]
    if len(wwa.index) > 4:
        box1 = [0.1, 0.15, 0.82, 0.55]
        box2 = [0.1, 0.7, 0.82, 0.2]
    ax = fig.add_axes(box1)
    top_ax = fig.add_axes(box2, frame_on=False)
    if ctx["mode"] == "BZ":
        obs = obs[pd.notna(obs["max_wind"]) & pd.notna(obs["vsby"])]
        plot_bz(ax, obs)
        fig.text(
            0.5,
            0.04,
            (
                "Gray Shaded areas <=1/4 mile vis & "
                "35+ MPH winds, Light Blue >= 3 Hours"
            ),
            ha="center",
        )
    elif ctx["mode"] in ["WC", "HT"]:
        obs = obs[pd.notna(obs["feel"])]
        plot(ax, obs, "feel")
    for i, row in wwa.iterrows():
        color = NWS_COLORS[row["key"]]
        ax.axvspan(
            row["utc_issue"],
            row["utc_expire"],
            color=color,
            zorder=1,
            alpha=0.4,
        )
        ax.axvline(row["utc_issue"], lw=2, zorder=2, color=color)
        ax.axvline(row["utc_expire"], lw=2, zorder=2, color=color)
        delta = row["utc_expire"] - row["utc_issue"]
        top_ax.plot(
            [
                row["utc_issue"],
                row["utc_issue"],
                row["utc_expire"],
                row["utc_expire"],
            ],
            [0, i + 1, i + 1, 0],
            lw=2,
            c=color,
        )
        xloc = row["utc_issue"] + delta / 2
        ha = "center"
        if xloc > ets:
            xloc = row["utc_issue"]
            ha = "left"
        top_ax.text(
            xloc,
            i + 0.5,
            f"{get_ps_string(*row['key'].split('.'))} #{row['eventid']}",
            va="center",
            ha=ha,
            color=color,
        )
    ax.grid(True)
    top_ax.set_ylim(0, len(wwa.index) + 1)
    top_ax.set_xticks([])
    top_ax.set_yticks([])
    tzinfo = ZoneInfo(ctx["_nt"].sts[station]["tzname"])
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=tzinfo))
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("|\n%d %b %Y", tz=tzinfo)
    )

    byhour = (
        [6, 12, 18]
        if ctx["hours"] < 73
        else [
            12,
        ]
    )
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=byhour, tz=tzinfo))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%I %p", tz=tzinfo))
    ax.set_xlabel(
        f"{sts.astimezone(tzinfo):%-d %b %Y %-H:%M %p} to "
        f"{ets.astimezone(tzinfo):%-d %b %Y %-H:%M %p} [{tzname}]"
    )
    ax.set_xlim(sts, ets + datetime.timedelta(minutes=5))
    top_ax.set_xlim(sts, ets + datetime.timedelta(minutes=5))

    return fig, obs
