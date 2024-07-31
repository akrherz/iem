"""
This autoplot presents a time series of UTC daily PIREP totals by ARTCC
or Alaska Zone.  The chart presents daily totals for PIREPs that contain
icing (/IC), turbulence (/TB), icing or turbulence and all reports.</p>

<p>Each chart presents a simple average over the plot and a trailing
30 day average.
"""

from datetime import date, timedelta

import matplotlib.dates as mdates
import pandas as pd
from pyiem.exceptions import NoDataFound
from pyiem.plot import figure
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn, utc
from sqlalchemy import text

# select distinct '"'||ident||'": "['||ident||'] '||name||'",' from airspaces
# where type_code in ('AKZONE', 'ARTCC');
PDICT = {
    "AB": "[AB] Cook Inlet and Susitna Valley",
    "AC": "[AC] Copper River Basin",
    "AD": "[AD] Central Gulf Coast",
    "AE": "[AE] Kodiak Island",
    "AF": "[AF] Kuskokwim Valley",
    "AG": "[AG] Yukon - Kuskokwim Delta",
    "AH": "[AH] Bristol Bay",
    "AI": "[AI] Alaska Peninsula",
    "AJ": "[AJ] Unimak Pass to Adak",
    "AK": "[AK] Adak to Attu",
    "AL": "[AL] Pribilof Islands and Southeast Bering Sea",
    "FB": "[FB] Upper Yukon Valley",
    "FC": "[FC] Tanana Valley",
    "FE": "[FE] Koyukuk and Upper Kobuk Valley",
    "FF": "[FF] Lower Yukon Valley",
    "FG": "[FG] Arctic Slope Coastal",
    "FH": "[FH] North Slopes of the Brooks Range",
    "FI": "[FI] Northern Seward Peninsula and Lower Kobuk Valley",
    "FJ": "[FJ] Southern Seward Peninsula and Eastern Norton Sound",
    "FK": "[FK] St. Lawrence Island and Western Norton Sound",
    "JB": "[JB] Lynn Canal and Glacier Bay",
    "JC": "[JC] Central Southeast Alaska",
    "JD": "[JD] Southern Southeast Alaska",
    "JE": "[JE] Eastern Gulf Coast",
    "JF": "[JF] Southeast Alaska Coastal Waters",
    "ZAB": "[ZAB] ALBUQUERQUE",
    "ZAN": "[ZAN] ANCHORAGE",
    "ZAU": "[ZAU] CHICAGO",
    "ZBW": "[ZBW] BOSTON ",
    "ZDC": "[ZDC] WASHINGTON",
    "ZDV": "[ZDV] DENVER",
    "ZFW": "[ZFW] FORT WORTH",
    "ZHU": "[ZHU] HOUSTON",
    "ZID": "[ZID] INDIANAPOLIS",
    "ZJX": "[ZJX] JACKSONVILLE",
    "ZKC": "[ZKC] KANSAS CITY",
    "ZLA": "[ZLA] LOS ANGELES",
    "ZLC": "[ZLC] SALT LAKE CITY",
    "ZMA": "[ZMA] MIAMI",
    "ZME": "[ZME] MEMPHIS",
    "ZMP": "[ZMP] MINNEAPOLIS",
    "ZNY": "[ZNY] NEW YORK",
    "ZOA": "[ZOA] OAKLAND",
    "ZOB": "[ZOB] CLEVELAND ",
    "ZSE": "[ZSE] SEATTLE",
    "ZTL": "[ZTL] ATLANTA",
    "_ALL": "All PIREPS / No Spatial Limit",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"cache": 86400, "description": __doc__, "data": True}
    today = date.today() + timedelta(days=1)
    t365 = today - timedelta(days=365)

    desc["arguments"] = [
        dict(
            type="select",
            name="ident",
            options=PDICT,
            default="ZMP",
            label="Select ARTCC/Alaska Zone:",
        ),
        dict(
            type="date",
            name="sdate",
            default=t365.strftime("%Y/%m/%d"),
            label="Start UTC Date (inclusive):",
            min="2003/03/01",
        ),
        dict(
            type="date",
            name="edate",
            default=today.strftime("%Y/%m/%d"),
            label="End UTC Date (inclusive):",
            min="2003/03/01",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    sdate = ctx["sdate"]
    edate = ctx["edate"]
    limiter = (
        ", airspaces a WHERE ST_Intersects(p.geom, a.geom) and "
        "a.ident = :ident and a.type_code in ('AKZONE', 'ARTCC') and "
    )
    if ctx["ident"] == "_ALL":
        limiter = " WHERE "
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
            SELECT date(valid at time zone 'UTC') as date, count(*),
            sum(case when substring(report, '/IC([^/]*)/') is not null then 1
                else 0 end) as icing_count,
            sum(case when substring(report, '/TB([^/]*)/') is not null then 1
                else 0 end) as turbulence_count,
            sum(case when
                substring(report, '/IC([^/]*)/') is not null and
                substring(report, '/TB([^/]*)/') is not null then 1
                else 0 end) as ice_and_turb_count
            from pireps p{limiter} valid >= :sts and valid <= :ets
            GROUP by date ORDER by date ASC
            """
            ),
            conn,
            params={
                "ident": ctx["ident"],
                "sts": utc(sdate.year, sdate.month, sdate.day),
                "ets": utc(edate.year, edate.month, edate.day, 23, 59),
            },
            index_col="date",
            parse_dates="date",
        )
    if df.empty:
        raise NoDataFound("Failed to find any PIREPs for query.")
    df = df.reindex(pd.date_range(sdate, edate)).fillna(0)
    tt = "ARTCC" if len(ctx["ident"]) == 3 else "Alaska"
    title = f"{PDICT[ctx['ident']]} {tt}"
    if ctx["ident"] == "_ALL":
        title = "All US + Canada"
    fig = figure(
        title=(
            f"{title} PIREP UTC Daily Counts "
            f"{sdate:%-d %b %Y} - {edate:%-d %b %Y}"
        ),
        subtitle="Based on unofficial IEM archives of parsed NWS PIREPs",
        apctx=ctx,
    )
    height = 0.18
    axes = [
        fig.add_axes([0.1, 0.1, 0.8, height]),
        fig.add_axes([0.1, 0.3, 0.8, height]),
        fig.add_axes([0.1, 0.5, 0.8, height]),
        fig.add_axes([0.1, 0.7, 0.8, height]),
    ]

    ylabels = [
        "All PIREPs",
        "Icing + Turbulence",
        "Turbulence Only",
        "Icing Only",
    ]
    cols = [
        "count",
        "ice_and_turb_count",
        "turbulence_count",
        "icing_count",
    ]
    colors = ["orange", "green", "red", "blue"]
    for i, (ax, col) in enumerate(zip(axes, cols)):
        axes[i].bar(
            df.index.values,
            df[col],
            color=colors[i],
        )
        axes[i].plot(
            df.index.values,
            df[col].rolling(30).mean(),
            color="brown",
            lw=2,
            label="30 Day Trail Ave" if i == 3 else "",
        )
        avgv = df[col].mean()
        axes[i].axhline(avgv, lw=2, color="k", label="Ave" if i == 3 else "")
        axes[i].annotate(
            f"Ave: {avgv:.1f}",
            (1, avgv),
            xycoords=("axes fraction", "data"),
            ha="left",
        )
        axes[i].set_ylabel(ylabels[i])
        ax.grid(True)
        if i > 0:
            ax.set_xticklabels([])
        ax.set_xlim(sdate, edate + timedelta(days=1))

    axes[3].legend(loc=(0.8, 1), ncol=2)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%-d %b\n%Y"))

    return fig, df
