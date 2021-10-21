"""LSR map by WFO"""
import datetime

import numpy as np
from pandas.io.sql import read_sql
import pytz
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import get_autoplot_context, get_dbconn

MDICT = dict(
    [
        ("NONE", "All LSR Types"),
        ("NRS", "All LSR Types except HEAVY RAIN + SNOW"),
        ("H1", "One Inch and Larger Hail "),
        ("CON", "Convective LSRs (Tornado, TStorm Gst/Dmg, Hail)"),
        ("AVALANCHE", "AVALANCHE"),
        ("BLIZZARD", "BLIZZARD"),
        ("COASTAL FLOOD", "COASTAL FLOOD"),
        ("DEBRIS FLOW", "DEBRIS FLOW"),
        ("DENSE FOG", "DENSE FOG"),
        ("DOWNBURST", "DOWNBURST"),
        ("DUST STORM", "DUST STORM"),
        ("EXCESSIVE HEAT", "EXCESSIVE HEAT"),
        ("EXTREME COLD", "EXTREME COLD"),
        ("EXTR WIND CHILL", "EXTR WIND CHILL"),
        ("FLASH FLOOD", "FLASH FLOOD"),
        ("FLOOD", "FLOOD"),
        ("FOG", "FOG"),
        ("FREEZE", "FREEZE"),
        ("FREEZING DRIZZLE", "FREEZING DRIZZLE"),
        ("FREEZING RAIN", "FREEZING RAIN"),
        ("FUNNEL CLOUD", "FUNNEL CLOUD"),
        ("HAIL", "HAIL"),
        ("HEAVY RAIN", "HEAVY RAIN"),
        ("HEAVY SLEET", "HEAVY SLEET"),
        ("HEAVY SNOW", "HEAVY SNOW"),
        ("HIGH ASTR TIDES", "HIGH ASTR TIDES"),
        ("HIGH SURF", "HIGH SURF"),
        ("HIGH SUST WINDS", "HIGH SUST WINDS"),
        ("HURRICANE", "HURRICANE"),
        ("ICE STORM", "ICE STORM"),
        ("LAKESHORE FLOOD", "LAKESHORE FLOOD"),
        ("LIGHTNING", "LIGHTNING"),
        ("LOW ASTR TIDES", "LOW ASTR TIDES"),
        ("MARINE TSTM WIND", "MARINE TSTM WIND"),
        ("NON-TSTM WND DMG", "NON-TSTM WND DMG"),
        ("NON-TSTM WND GST", "NON-TSTM WND GST"),
        ("RAIN", "RAIN"),
        ("RIP CURRENTS", "RIP CURRENTS"),
        ("SLEET", "SLEET"),
        ("SNOW", "SNOW"),
        ("STORM SURGE", "STORM SURGE"),
        ("TORNADO", "TORNADO"),
        ("TROPICAL STORM", "TROPICAL STORM"),
        ("TSTM WND DMG", "TSTM WND DMG"),
        ("TSTM WND GST", "TSTM WND GST"),
        ("WALL CLOUD", "WALL CLOUD"),
        ("WATER SPOUT", "WATER SPOUT"),
        ("WILDFIRE", "WILDFIRE"),
    ]
)
PDICT = dict([("wfo", "By NWS Forecast Office"), ("state", "By State")])


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """This application generates a map displaying the
    number of LSRs issued between a period of your choice by NWS Office. These
    are the preliminary reports and not official totals of events."""
    today = datetime.date.today() + datetime.timedelta(days=1)
    jan1 = today.replace(month=1, day=1)
    desc["arguments"] = [
        dict(
            type="datetime",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d 0000"),
            label="Start Date / Time (UTC, inclusive):",
            min="2006/01/01 0000",
        ),
        dict(
            type="datetime",
            name="edate",
            default=today.strftime("%Y/%m/%d 0000"),
            label="End Date / Time (UTC):",
            min="2006/01/01 0000",
        ),
        dict(
            type="select",
            name="filter",
            default="NONE",
            options=MDICT,
            label="Local Storm Report Type Filter",
        ),
        dict(
            type="select",
            name="by",
            default="wfo",
            label="Aggregate Option:",
            options=PDICT,
        ),
        dict(type="cmap", name="cmap", default="plasma", label="Color Ramp:"),
    ]
    return desc


def plotter(fdict):
    """Go"""
    pgconn = get_dbconn("postgis")
    ctx = get_autoplot_context(fdict, get_description())
    sts = ctx["sdate"]
    sts = sts.replace(tzinfo=pytz.utc)
    ets = ctx["edate"]
    by = ctx["by"]
    ets = ets.replace(tzinfo=pytz.utc)
    myfilter = ctx["filter"]
    if myfilter == "NONE":
        tlimiter = ""
    elif myfilter == "NRS":
        tlimiter = " and typetext not in ('HEAVY RAIN', 'SNOW', 'HEAVY SNOW') "
    elif myfilter == "H1":
        tlimiter = " and typetext = 'HAIL' and magnitude >= 1 "
    elif myfilter == "CON":
        tlimiter = (
            " and typetext in ('TORNADO', 'HAIL', 'TSTM WND GST', "
            "'TSTM WND DMG') "
        )
    else:
        tlimiter = " and typetext = '%s' " % (myfilter,)

    df = read_sql(
        f"""
    WITH data as (
        SELECT distinct wfo, state, valid, type, magnitude, geom from lsrs
        where valid >= %s and valid < %s {tlimiter}
    )
    SELECT {by}, count(*) from data GROUP by {by}
    """,
        pgconn,
        params=(sts, ets),
        index_col=by,
    )
    data = {}
    for idx, row in df.iterrows():
        if idx == "JSJ":
            idx = "SJU"
        data[idx] = row["count"]
    maxv = df["count"].max()
    bins = np.linspace(1, maxv, 12, dtype="i")
    bins[-1] += 1
    mp = MapPlot(
        twitter=True,
        sector="nws",
        axisbg="white",
        title=f"Preliminary/Unfiltered Local Storm Report Counts {PDICT[by]}",
        subtitlefontsize=10,
        subtitle=("Valid %s - %s UTC, type limiter: %s")
        % (
            sts.strftime("%d %b %Y %H:%M"),
            ets.strftime("%d %b %Y %H:%M"),
            MDICT.get(myfilter),
        ),
    )
    cmap = get_cmap(ctx["cmap"])
    if by == "wfo":
        mp.fill_cwas(data, bins=bins, lblformat="%.0f", cmap=cmap, ilabel=True)
    else:
        mp.fill_states(
            data, bins=bins, lblformat="%.0f", cmap=cmap, ilabel=True
        )

    return mp.fig, df


if __name__ == "__main__":
    plotter(dict())
