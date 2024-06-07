"""
This autoplot generates a calendar showing calendar day Local Storm
Report totals by NWS Weather Forecast Office (WFO) or State.  The calendar
date is based on the local timezone of the WFO selected.  The calendar plot
type only supports up to 12 months plotted at once.
"""

import datetime

import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import calendar_plot
from pyiem.reference import state_names
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

PDICT = {"yes": "Colorize Cells in Chart", "no": "Just plot values please"}
MDICT = {
    "NONE": "All LSR Types",
    "NRS": "All LSR Types except HEAVY RAIN + SNOW",
    "H1": "One Inch and Larger Hail ",
    "CON": "Convective LSRs (Tornado, TStorm Gst/Dmg, Hail)",
    "AVALANCHE": "AVALANCHE",
    "BLIZZARD": "BLIZZARD",
    "COASTAL FLOOD": "COASTAL FLOOD",
    "DEBRIS FLOW": "DEBRIS FLOW",
    "DENSE FOG": "DENSE FOG",
    "DOWNBURST": "DOWNBURST",
    "DUST STORM": "DUST STORM",
    "EXCESSIVE HEAT": "EXCESSIVE HEAT",
    "EXTREME COLD": "EXTREME COLD",
    "EXTR WIND CHILL": "EXTR WIND CHILL",
    "FLASH FLOOD": "FLASH FLOOD",
    "FLOOD": "FLOOD",
    "FOG": "FOG",
    "FREEZE": "FREEZE",
    "FREEZING DRIZZLE": "FREEZING DRIZZLE",
    "FREEZING RAIN": "FREEZING RAIN",
    "FUNNEL CLOUD": "FUNNEL CLOUD",
    "HAIL": "HAIL",
    "HEAVY RAIN": "HEAVY RAIN",
    "HEAVY SLEET": "HEAVY SLEET",
    "HEAVY SNOW": "HEAVY SNOW",
    "HIGH ASTR TIDES": "HIGH ASTR TIDES",
    "HIGH SURF": "HIGH SURF",
    "HIGH SUST WINDS": "HIGH SUST WINDS",
    "HURRICANE": "HURRICANE",
    "ICE STORM": "ICE STORM",
    "LAKESHORE FLOOD": "LAKESHORE FLOOD",
    "LIGHTNING": "LIGHTNING",
    "LOW ASTR TIDES": "LOW ASTR TIDES",
    "MARINE TSTM WIND": "MARINE TSTM WIND",
    "NON-TSTM WND DMG": "NON-TSTM WND DMG",
    "NON-TSTM WND GST": "NON-TSTM WND GST",
    "RAIN": "RAIN",
    "RIP CURRENTS": "RIP CURRENTS",
    "SLEET": "SLEET",
    "SNOW": "SNOW",
    "STORM SURGE": "STORM SURGE",
    "TORNADO": "TORNADO",
    "TROPICAL STORM": "TROPICAL STORM",
    "TSTM WND DMG": "TSTM WND DMG",
    "TSTM WND GST": "TSTM WND GST",
    "WALL CLOUD": "WALL CLOUD",
    "WATER SPOUT": "WATER SPOUT",
    "WILDFIRE": "WILDFIRE",
}
PDICT2 = {"cwa": "by NWS Forecast Office", "state": "by State"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    today = datetime.date.today()
    jan1 = today.replace(month=1, day=1)
    desc["arguments"] = [
        dict(
            type="date",
            name="sdate",
            default=jan1.strftime("%Y/%m/%d"),
            label="Start Date (inclusive):",
            min="1986/01/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End Date (inclusive):",
            min="1986/01/01",
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
            name="w",
            options=PDICT2,
            default="cwa",
            label="Plot stats for:",
        ),
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            all=True,
            default="DMX",
            label="Select WFO (when appropriate):",
        ),
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State (when appropriate):",
        ),
        dict(
            type="select",
            name="heatmap",
            options=PDICT,
            default="yes",
            label="Colorize calendar cells based on values?",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    sts = ctx["sdate"]
    ets = ctx["edate"]
    if (ets - sts).days > 366:
        raise NoDataFound("Chart duration needs to be less than 1 year.")
    wfo = ctx["wfo"]
    state = ctx["state"]
    params = {}
    params["tzname"] = ctx["_nt"].sts[wfo]["tzname"]
    params["sts"] = sts - datetime.timedelta(days=2)
    params["ets"] = ets + datetime.timedelta(days=2)

    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    if wfo not in ctx["_nt"].sts:
        raise NoDataFound("No Data Found.")
    params["wfo"] = wfo if len(wfo) == 3 else wfo[1:]
    wfo_limiter = ""
    if ctx["w"] == "cwa":
        wfo_limiter = " and wfo = :wfo "
        if wfo == "_ALL":
            wfo_limiter = ""
        title2 = f"NWS {ctx['_sname']}"
        if wfo == "_ALL":
            title2 = "All NWS Offices"
    else:
        wfo_limiter = " and state = :state "
        params["state"] = state
        title2 = f"{state_names[state]}"

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
        tlimiter = f" and typetext = '{myfilter}' "
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
                WITH data as (
                    SELECT distinct wfo, state,
                    valid at time zone :tzname as valid, magnitude, typetext,
                    city
                    from lsrs l where valid >= :sts and valid < :ets {tlimiter}
                    {wfo_limiter}
                )
                SELECT date(valid), count(*) from data GROUP by date
                ORDER by date ASC
        """
            ),
            conn,
            params=params,
            index_col="date",
        )

    data = {}
    now = sts
    while now <= ets:
        data[now] = {"val": 0}
        now += datetime.timedelta(days=1)
    for date, row in df.iterrows():
        data[date] = {"val": row["count"]}
    fig = calendar_plot(
        sts,
        ets,
        data,
        apctx=ctx,
        heatmap=(ctx["heatmap"] == "yes"),
        title=f"{title2} :: Preliminary/Unfiltered Local Storm Reports",
        subtitle=(
            f"Valid {sts:%d %b %Y} - {ets:%d %b %Y} "
            f"type limiter: {MDICT.get(myfilter)}"
        ),
    )
    return fig, df


if __name__ == "__main__":
    plotter({})
