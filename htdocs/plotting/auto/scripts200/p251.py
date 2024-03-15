"""
The purpose of this autoplot is to generate a time series of NWS warning load
with time for short fuse warnings.
"""

from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.nws.vtec import NWS_COLORS
from pyiem.plot import figure_axes
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 300}
    utcnow = utc()
    desc["arguments"] = [
        {
            "type": "networkselect",
            "name": "wfo",
            "all": True,
            "label": "Select WFO:",
            "default": "_ALL",
            "network": "WFO",
        },
        {
            "type": "datetime",
            "name": "sts",
            "default": f"{utcnow - timedelta(days=1):%Y/%m/%d %H00}",
            "label": "Start Time (UTC):",
            "min": "1986/01/01 0000",
            "max": utc().strftime("%Y/%m/%d 2359"),
        },
        {
            "type": "datetime",
            "name": "ets",
            "default": f"{utcnow:%Y/%m/%d %H%M}",
            "label": "End Time (UTC) (period less than 96 hours):",
            "min": "1986/01/01 0000",
            "max": utc().strftime("%Y/%m/%d 2359"),
        },
    ]
    return desc


def getp(conn, phenomena, wfo, sts, ets):
    """Do Query"""
    wfolimiter = "" if wfo == "_ALL" else " and wfo = :wfo "
    params = {
        "wfo": wfo,
        "ssts": sts - timedelta(hours=12),
        "sts": sts,
        "ets": ets,
        "phenomena": phenomena,
    }
    res = conn.execute(
        text(f"""
     WITH data as (
        select distinct vtec_year, wfo, eventid, phenomena,
        generate_series(issue, expire, '1 minute'::interval) as t
        from warnings where issue > :ssts and
        issue < :ets and phenomena = :phenomena and significance = 'W'
             {wfolimiter}),
    agg as (
        SELECT t, count(*) from data GROUP by t
    ),
     ts as (
        select generate_series(:sts, :ets, '1 minute'::interval) as t
    )

     SELECT ts.t at time zone 'UTC' as utc_valid,
     coalesce(agg.count, 0) as cnt from ts
     LEFT JOIN agg on (ts.t = agg.t)
     ORDER by ts.t ASC
    """),
        params,
    )
    times = []
    counts = []
    for row in res:
        times.append(row[0])
        counts.append(row[1])

    return times, counts


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    wfo = ctx["wfo"]
    sts = ctx["sts"].replace(tzinfo=timezone.utc)
    ets = ctx["ets"].replace(tzinfo=timezone.utc)
    if (ets - sts) > timedelta(days=4):
        raise IncompleteWebRequest("Sorry, period must be less than 96 hours.")
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    tzinfo = ZoneInfo(ctx["_nt"].sts[wfo]["tzname"])

    with get_sqlalchemy_conn("postgis") as conn:
        to_t, to_c = getp(conn, "TO", wfo, sts, ets)
        _, sv_c = getp(conn, "SV", wfo, sts, ets)
        _, ff_c = getp(conn, "FF", wfo, sts, ets)
    df = pd.DataFrame({"valid": to_t, "tor": to_c, "svr": sv_c, "ffw": ff_c})
    df["valid"] = df["valid"].dt.tz_localize(ZoneInfo("UTC"))
    df = df.set_index("valid")
    df["tor_ffw"] = df["tor"] + df["ffw"]
    df["all"] = df["tor"] + df["ffw"] + df["svr"]
    df["svr_tor"] = df["svr"] + df["tor"]

    lt0 = df.index[1].tz_convert(tzinfo)
    lt1 = df.index[-5].tz_convert(tzinfo)
    if lt0.day == lt1.day:
        datetitle = lt0.strftime("%-d %b %Y")
    else:
        datetitle = f"{lt0.strftime('%-d %b')} to {lt1.strftime('%-d %b %Y')}"

    (fig, ax) = figure_axes(
        title=(
            f"{datetitle} NWS {ctx['_nt'].sts[wfo]['name']}:: "
            "Storm Based Warning Load"
        ),
        subtitle="Unofficial IEM Archives, presented as a stacked bar chart",
        apctx=ctx,
    )

    ax.bar(
        df.index,
        df["all"],
        width=1 / 1440.0,
        color=NWS_COLORS["SV.W"],
        label="Severe T'Storm",
    )
    ax.bar(
        df.index,
        df["tor_ffw"],
        width=1 / 1440.0,
        color=NWS_COLORS["TO.W"],
        label="Tornado",
    )
    ax.bar(
        df.index,
        df["ffw"],
        width=1 / 1440.0,
        color="g",  # Eh
        label="Flash Flood",
    )
    if (ets - sts) < timedelta(days=2):
        ax.plot(
            df.index,
            df["all"],
            color="k",
            drawstyle="steps-post",
        )
        ax.plot(
            df.index,
            df["tor_ffw"],
            color="k",
            drawstyle="steps-post",
        )
        ax.plot(
            df.index,
            df["ffw"],
            color="k",
            drawstyle="steps-post",
        )

    ax.grid(True)
    hours = range(0, 24, 3)
    fmt = "%-I %p"
    if (ets - sts) > timedelta(days=2):
        hours = range(0, 24, 12)
        fmt = "%-I %p\n%-d %b"
    elif (ets - sts) > timedelta(days=1):
        hours = range(0, 24, 6)
        fmt = "%-I %p\n%-d %b"
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=hours, tz=tzinfo))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt, tz=tzinfo))

    ax.set_ylabel("Total Warning Count (SVR+TOR+FFW)")
    ax.legend(loc=1, ncol=2)
    ax.set_ylim(bottom=0.1, top=df["all"].max() * 1.3)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_xlim(sts, ets)
    ax.set_xlabel(f"Timezone: {ctx['_nt'].sts[wfo]['tzname']}")

    def ff(val):
        """Format"""
        bah = fmt.replace("\n", " ").replace("%-I", "%-I:%M")
        return val.astimezone(tzinfo).strftime(bah)

    ax.annotate(
        f"TOR+SVR+FFW Max: {df['all'].max()} @{ff(df['all'].idxmax())}"
        f"\nTOR+SVR Max: {df['svr_tor'].max()} @{ff(df['svr_tor'].idxmax())}"
        f"\nTOR Max: {df['tor'].max()} @{ff(df['tor'].idxmax())}"
        f"\nSVR Max: {df['svr'].max()} @{ff(df['svr'].idxmax())}"
        f"\nFFW Max: {df['ffw'].max()} @{ff(df['ffw'].idxmax())}",
        xy=(0.01, 0.99),
        xycoords="axes fraction",
        bbox=dict(facecolor="white"),
        ha="left",
        va="top",
    )

    return fig, df.reset_index()


if __name__ == "__main__":
    plotter({})
