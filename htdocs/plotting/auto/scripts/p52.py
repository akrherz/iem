"""
Gantt chart of watch, warning, and advisories (WaWa) issued
by an NWS Forecast Office for a start date and number of days of your
choice.

<p>The width of the bar is the duration of the event and is a bit difficult
to explain for some WaWa types.  The color shaded area represents the maximum
period at least one county/zone was included in the event.  The hallow area
represents the period between when the NWS created the event to when it
first hit its issuance time.  This is a quirk of how VTEC works with things
like winter storm watches going "into effect" at some time in the future. When
there is no hallow area, these are events that went into effect immediately
at issuance.  For example, Severe Thunderstorm Warnings are all this way.
"""

import datetime
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import ticker
from matplotlib.patches import Rectangle
from pyiem.exceptions import NoDataFound
from pyiem.nws import vtec
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "cache": 600, "data": True}
    desc["arguments"] = [
        dict(
            type="networkselect",
            name="station",
            network="WFO",
            default="DMX",
            label="Select WFO:",
        ),
        dict(
            type="date",
            name="sdate",
            default="2015/01/01",
            label="Start Date:",
            min="2005/10/01",
        ),
        dict(
            type="int", name="days", default=10, label="Number of Days in Plot"
        ),
    ]
    return desc


def make_key(fig):
    """Make a cartoon in the lower right corner to illustrate bar."""
    ax = fig.add_axes([0, 0, 1, 1], frameon=False, zorder=-1)
    ax.text(0.81, 0.16, "Details of bar", fontsize=10)
    ax.add_patch(
        Rectangle(
            (0.80, 0.1),
            0.15,
            0.05,
            fc="None",
            ec="k",
            zorder=5,
        )
    )
    ax.text(0.84, 0.12, "Event\nCreated", fontsize=8, ha="center", va="center")
    ax.add_patch(
        Rectangle(
            (0.87, 0.1),
            0.08,
            0.05,
            color=vtec.NWS_COLORS.get("WC.Y"),
            zorder=4,
        )
    )
    ax.text(
        0.91,
        0.12,
        "Min Issue to\nMax Expire",
        fontsize=8,
        ha="center",
        va="center",
        zorder=6,
    )


def make_url(row, state):
    """Turn it into a URL"""
    wfo = f"K{row['wfo']}"
    if state in ["AK", "HI", "GU"]:
        wfo = f"P{row['wfo']}"
    elif state in ["PR"]:
        wfo = f"T{row['wfo']}"
    return (
        f"https://mesonet.agron.iastate.edu/vtec/f/{row['year']}-O-NEW-{wfo}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04d}"
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    station = ctx["station"]
    sts = ctx["sdate"]
    if station not in ctx["_nt"].sts:
        raise NoDataFound("Invalid station provided.")
    tz = ZoneInfo(ctx["_nt"].sts[station]["tzname"])
    sts = datetime.datetime(sts.year, sts.month, sts.day, tzinfo=tz)
    days = ctx["days"]

    ets = sts + datetime.timedelta(days=days)
    params = {"wfo": station, "sts": sts, "ets": ets}
    date_cols = ["minproductissue", "minissue", "maxexpire", "maxinitexpire"]
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                """
            SELECT phenomena, significance, eventid,
            min(product_issue at time zone 'UTC') as minproductissue,
            min(issue at time zone 'UTC') as minissue,
            max(expire at time zone 'UTC') as maxexpire,
            max(coalesce(init_expire, expire) at time zone 'UTC')
                as maxinitexpire,
            extract(year from product_issue)::int as year
            from warnings
            WHERE wfo = :wfo and issue > :sts and issue < :ets
            GROUP by phenomena, significance, eventid, year
            ORDER by minproductissue ASC
        """
            ),
            conn,
            params=params,
            index_col=None,
            parse_dates=date_cols,
        )
    if df.empty:
        raise NoDataFound("No events were found for WFO and time period.")
    for col in date_cols:
        df[col] = df[col].dt.tz_localize(ZoneInfo("UTC"))
    df["wfo"] = station
    df["endts"] = df[["maxexpire", "maxinitexpire"]].max(axis=1)
    # Flood warnings, for example, could have an issuance until-further-notice
    # which is not helpful for this plot, so don't allow a maxinitexpire
    # to be 5 days greater than the maxexpire
    df.loc[
        (df["maxinitexpire"] - df["maxexpire"]).dt.total_seconds() > 432000,
        "endts",
    ] = df["maxexpire"]
    df["label"] = df.apply(
        lambda x: vtec.get_ps_string(x["phenomena"], x["significance"]),
        axis=1,
    )
    df["duration_secs"] = (
        (df["endts"] - df["minissue"]).dt.total_seconds().astype("int")
    )
    state = ctx["_nt"].sts[station]["state"]
    df["link"] = df.apply(lambda x: make_url(x, state), axis=1)
    # If we have lots of WWA, we need to expand vertically a bunch, lets
    # assume we can plot 5 WAA per 100 pixels
    title = (
        f"NWS {ctx['_nt'].sts[station]['name']} "
        "issued Watch/Warning/Advisories\n"
        f"{sts:%-d %b %Y} through "
        f"{(ets - datetime.timedelta(days=1)):%-d %b %Y}"
    )
    fig = figure(title=title, apctx=ctx)
    ax = fig.add_axes([0.07, 0.09, 0.71, 0.81])
    fontsize = 8 if len(df.index) > 20 else 10

    used = []

    for i, row in df.iterrows():
        phsig = f"{row['phenomena']}.{row['significance']}"
        ax.barh(
            i + 1,
            row["duration_secs"] / 86400.0,
            left=row["minissue"],
            align="center",
            fc=vtec.NWS_COLORS.get(phsig, "k"),
            ec=vtec.NWS_COLORS.get(phsig, "k"),
            label=None if phsig in used else row["label"],
            zorder=3,
        )
        if row["minissue"] != row["minproductissue"]:
            # Draw a empty bar with black outline
            duration = (
                row["endts"] - row["minproductissue"]
            ).total_seconds() / 86400.0
            ax.barh(
                i + 1,
                duration,
                left=row["minproductissue"],
                align="center",
                fc="None",
                ec="k",
                label=None,
                zorder=4,
            )
        used.append(phsig)
        # Figure out where there is room for the label to go.
        x1 = (row["endts"] - sts).total_seconds() / (86400.0 * days)
        # place to the right if end of bar is less than 70% of the way
        if x1 < 0.7:
            align = "left"
            xpos = row["endts"] + datetime.timedelta(minutes=90)
        else:
            align = "right"
            xpos = row["minproductissue"] - datetime.timedelta(minutes=90)
        textcolor = vtec.NWS_COLORS.get(phsig if phsig != "TO.A" else "X", "k")
        ax.text(
            xpos,
            i + 1,
            row["label"].replace("Weather", "Wx") + " " + str(row["eventid"]),
            color=textcolor,
            ha=align,
            va="center",
            bbox=dict(color="white", boxstyle="square,pad=0"),
            fontsize=fontsize,
        )

    ax.set_ylabel("Sequential Product Issuance")

    ax.set_ylim(0, len(df.index) + 1)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1, tz=tz))
    xinterval = int(days / 7) + 1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=xinterval, tz=tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b", tz=tz))

    ax.grid(True)

    ax.set_xlim(sts, ets)
    ax.set_xlabel(f"Timezone: {ctx['_nt'].sts[station]['tzname']}")

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.0, 1.0),
        fancybox=True,
        shadow=True,
        ncol=1,
        scatterpoints=1,
        fontsize=8,
    )
    make_key(fig)
    # worried about breaking API
    for col in date_cols:
        df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
    return fig, df


if __name__ == "__main__":
    plotter({})
