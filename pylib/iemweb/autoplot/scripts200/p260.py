"""
This autoplot maps out the issued NWS Watch/Warning/Advisory events over a
given time period of your choice.  The displayed events are <strong>only
spatially filtered</strong> in the case of a per WFO or per State Map. The
spatial filter for the state level isn't necessarily straight forward and
an arbitrary choice was made to require 5% of the polygon area to reside
within the state for it to count.</p>

<p><a href="/plotting/auto/?q=90">Autoplot 90</a> is similar to this app, but
produces heatmaps and other summary maps.</p>
"""

from datetime import timedelta, timezone
from typing import TYPE_CHECKING

import geopandas as gpd
import pyiem.nws.vtec as vtec
from matplotlib.patches import Rectangle
from pyiem import reference
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import NoDataFound
from pyiem.nws.vtec import NWS_COLORS
from pyiem.plot import MapPlot
from pyiem.reference import (
    SECTORS,
    Z_OVERLAY2,
    fema_region_bounds,
    wfo_bounds,
)
from pyiem.util import load_geodf, utc

from iemweb.autoplot import ARG_FEMA, FEMA_REGIONS

if TYPE_CHECKING:
    import pandas as pd


PDICT = {
    "wfo": "Plot by NWS Forecast Office",
    "csector": "Plot by State / Region / US",
    "fema": "Plot by FEMA Region",
    "data": "Plot to Data Domain (contiguous US only)",
}
PDICT2 = {
    "single": "Plot Single Selected Phenomena / Significance",
    "svrtor": "Severe T'Storm + Tornado Warnings",
    "svrtorffw": "Severe T'Storm + Tornado + Flash Flood Warnings",
}
PDICT3 = {
    "cbw": "County Based Warnings",
    "sbw": "Storm Based Warnings",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True, "cache": 86400}
    sts = utc() - timedelta(days=1)
    desc["arguments"] = [
        {
            "type": "select",
            "options": PDICT3,
            "name": "geo",
            "default": "sbw",
            "label": "Select Warning Type",
        },
        dict(
            type="select",
            name="opt",
            default="wfo",
            options=PDICT,
            label="How to plot the data?",
        ),
        {
            "type": "datetime",
            "min": "1986/01/01 0000",
            "default": sts.strftime("%Y/%m/%d 0000"),
            "label": "Start Time (UTC) of event issuance:",
            "name": "sts",
        },
        {
            "type": "datetime",
            "min": "1986/01/01 0000",
            "default": utc().strftime("%Y/%m/%d 0000"),
            "label": "End Time (UTC) of event issuance (period &gt; 32 days):",
            "name": "ets",
        },
        dict(
            type="networkselect",
            name="wfo",
            network="WFO",
            default="DMX",
            label="Select WFO:",
            all=True,
        ),
        dict(
            type="csector",
            name="csector",
            default="conus",
            label="Select state/sector to plot",
        ),
        ARG_FEMA,
        {
            "type": "select",
            "options": PDICT2,
            "name": "c",
            "default": "single",
            "label": "Total by Selected Phenomena/Significance or Combo",
        },
        dict(
            type="phenomena",
            name="phenomena",
            default="FF",
            label="Select Watch/Warning Phenomena Type:",
        ),
        dict(
            type="significance",
            name="significance",
            default="W",
            label="Select Watch/Warning Significance Level:",
        ),
    ]
    return desc


def plotter(ctx: dict):
    """Go"""
    wfo = ctx["wfo"]
    phenomena = ctx["phenomena"]
    significance = ctx["significance"]
    opt = ctx["opt"]
    if opt == "all":
        opt = "wfo"
        wfo = "_ALL"
    csector = ctx.pop("csector")  # prevent apctx usage
    ctx["_nt"].sts["_ALL"] = {
        "name": "All Offices",
        "tzname": "America/Chicago",
    }
    if (ctx["ets"] - ctx["sts"]).days > 32:
        raise NoDataFound("Sorry, period is too long!")
    params = {
        "sts": ctx["sts"].replace(tzinfo=timezone.utc),
        "ets": ctx["ets"].replace(tzinfo=timezone.utc),
        "ph": [
            phenomena,
        ],
        "sig": significance,
    }
    wfo_limiter = ""
    if wfo == "_ALL":
        wfo_limiter = ""
        ctx["_sname"] = "All Offices"

    if opt == "csector":
        # Filtering is done later for non-state sectors
        if len(csector) == 2:
            if ctx["geo"] == "sbw":
                gdf = load_geodf("us_states")
                # Require at least 5% of the area to be within the state
                wfo_limiter = """
    and ST_Intersects(geom, ST_SetSRID(ST_GeomFromEWKT(:wkt), 4326)) and
    (ST_area(st_intersection(geom, ST_SetSRID(ST_GeomFromEWKT(:wkt), 4326))) /
     ST_area(geom)) > 0.05
                """
                params["wkt"] = gdf.at[csector, "geom"].wkt
            else:
                wfo_limiter = " and substr(w.ugc, 1, 2) = :state "
                params["state"] = csector
    elif opt == "wfo":
        wfo_limiter = " and w.wfo = :wfo "
        params["wfo"] = wfo if len(wfo) == 3 else wfo[1:]
    elif opt == "data":
        wfo_limiter = " and w.wfo not in ('AFC', 'AFG', 'GUM', 'JSJ', 'HFO') "

    if ctx["c"] == "svrtor":
        params["ph"] = ["SV", "TO"]
        params["sig"] = "W"
    elif ctx["c"] == "svrtorffw":
        params["ph"] = ["SV", "TO", "FF"]
        params["sig"] = "W"

    sql = """
            SELECT
            geom, wfo, phenomena, significance, eventid
            from sbw w where phenomena = ANY(:ph) and significance = :sig
            and status = 'NEW' and issue >= :sts and issue < :ets
            {wfo_limiter}
        """
    if ctx["geo"] == "cbw":
        sql = """
        select simple_geom as geom, w.wfo, phenomena, significance, eventid
        from warnings w JOIN ugcs u on (w.gid = u.gid)
        WHERE phenomena = ANY(:ph) and significance = :sig
        and issue >= :sts and issue < :ets {wfo_limiter}
        """

    with get_sqlalchemy_conn("postgis") as conn:
        wwadf: pd.DataFrame = gpd.read_postgis(
            sql_helper(sql, wfo_limiter=wfo_limiter),
            conn,
            params=params,
            index_col=None,
            geom_col="geom",
        )  # type: ignore

    if wwadf.empty:
        raise NoDataFound("Sorry, no data found!")

    subtitle = "Counts: "
    st = []
    legend_items = []
    for (ph, sig), gdf in wwadf.groupby(["phenomena", "significance"]):
        st.append(f"{len(gdf)} {vtec.get_ps_string(ph, sig)} ({ph}.{sig})")
        legend_items.append(
            Rectangle(
                (0, 0),
                1,
                1,
                fc=NWS_COLORS.get(f"{ph}.{sig}", "k"),
                ec="k",
                lw=1,
                label=vtec.get_ps_string(ph, sig),
            )
        )
    subtitle += ", ".join(st)

    title = (
        f"Issued between {ctx['sts']:%-d %b %Y %H:%M} and "
        f"{ctx['ets']:%-d %b %Y %H:%M} UTC "
    )
    bnds = wwadf.total_bounds
    if opt == "csector":
        if len(csector) == 2:
            title += f"for State of {reference.state_names[csector]}"
        else:
            title += f"for {SECTORS[csector]}"
    elif opt == "wfo":
        title += f"by {ctx['_sname']}"
        bnds = wfo_bounds[wfo]
    elif opt == "fema":
        title += f"for FEMA {FEMA_REGIONS[ctx['fema']]}"
        bnds = fema_region_bounds[int(ctx["fema"])]
    elif opt == "data":
        title += "for Contiguous US"

    mp = MapPlot(
        apctx=ctx,
        title=title,
        subtitle=subtitle,
        sector="spherical_mercator",
        west=bnds[0],
        east=bnds[2],
        south=bnds[1],
        north=bnds[3],
        nocaption=True,
    )
    wwadf["edgecolor"] = wwadf.apply(
        lambda x: NWS_COLORS.get(f"{x['phenomena']}.{x['significance']}", "k"),
        axis=1,
    )
    wwadf["facecolor"] = wwadf["edgecolor"] + "40"  # 25% opaque
    wwadf.to_crs(mp.panels[0].crs).plot(  # type: ignore
        ax=mp.ax,
        facecolor=wwadf["facecolor"].to_list(),
        edgecolor=wwadf["edgecolor"].to_list(),
        lw=2,
        aspect=None,
        zorder=Z_OVERLAY2,
    )
    mp.ax.legend(
        handles=legend_items,
        loc="upper right",
        fontsize=8,
    )

    return mp.fig, wwadf.drop(columns="geom")
