"""
This autoplot generates a map of active NWS Watch, Warnings, and Advisories
active at the given timestamp.

<p><strong>Footnote on "Active" WaWA</strong>: A more complex than it
should be nuance to explain here is the concept of what is "active" at
a given timestamp.  Let us consider a real world example.  On Monday
afternoon, the NWS issues a Winter Storm Warning for an upcoming
storm that goes "into effect" at noon on Tuesday.  You request this
plot for a timestamp of 6 PM on that Monday.  Is the Winter Storm
Warning included in this metric at that time?
<ul>
<li>Yes, if you select the option to include any WaWA that have been
created, but may have an VTEC start time in the future yet.</li>
<li>No, if you select the option to only include WaWA that have an
issuance time before the given timestamp.</li>
</ul>
<br />The default setting here is the first option, to include any events
that have been created, but not necessarily having an issuance time prior
to the given timestamp.  This is why we can't have nice things!</p>

<p>If you turn on statistics, the legend displays active events nationwide.
Central Region NWS maintains a
<a href="https://www.weather.gov/images/crh/dhs/wwa_population.png"
>similar map</a>, but is near real-time only.</p>

<p><a href="/plotting/auto/?q=224">Autoplot 224</a> is closely related to
this app and provides a table of stats.</p>
"""
from datetime import timezone
from io import StringIO

import geopandas as gpd
import httpx
import pandas as pd
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import NWS_COLORS, get_ps_string
from pyiem.plot import MapPlot
from pyiem.reference import SECTORS_NAME, Z_OVERLAY2, state_names
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

# shared with 224
PDICT = {
    "active": "Include WaWA that have been created or valid at the given time",
    "within": "Include WaWA with VTEC issuance time before the given time",
}
PDICT2 = {
    "none": "None",
    "stats": "Include Population and Area Statistics",
}
PDICT3 = {
    "yes": "Yes. Show counties",
    "no": "No. Do not show counties",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__}
    desc["defaults"] = {"_r": None}  # disables
    sectors = SECTORS_NAME.copy()
    sectors["nws"] = "NWS All"
    sectors.update(state_names)
    desc["arguments"] = [
        {
            "type": "datetime",
            "name": "valid",
            "default": utc().strftime("%Y/%m/%d %H00"),
            "label": "Valid Timestamp (UTC):",
            "min": "1986/01/01 0000",
        },
        {
            "type": "select",
            "options": PDICT,
            "default": "active",
            "name": "opt",
            "label": "How to consider if an event is active [see footnote]",
        },
        {
            "type": "select",
            "options": sectors,
            "name": "csector",
            "default": "nws",
            "label": "Select state/sector",
        },
        {
            "type": "select",
            "options": PDICT2,
            "name": "add",
            "default": "none",
            "label": "Include Statistics in Legend (slows down plot)",
        },
        {
            "type": "select",
            "options": PDICT3,
            "name": "sc",
            "default": "yes",
            "label": "Show Counties",
        },
    ]
    return desc


def plotsbw(mp, df):
    """Do sbw plotting."""
    df["color"] = df["ps"].apply(lambda x: NWS_COLORS.get(x, "k"))
    for panel in mp.panels:
        df2 = df.to_crs(panel.crs).cx[
            slice(*panel.get_xlim()), slice(*panel.get_ylim())
        ]

        if df2.empty:
            continue
        df2.plot(
            ax=panel.ax,
            aspect=None,
            edgecolor=df2["color"],
            facecolor="None",
            lw=2,
            zorder=Z_OVERLAY2 + 3,
        )


def get_ps(pstr):
    """."""
    return (
        get_ps_string(*pstr.split("."))
        .replace("Advisory", "Adv")
        .replace("Small Craft for", "SC")
    )


def make_legend(mp, df, statdf, year):
    """Do legend work."""
    if "zone_pop" not in statdf.columns:
        # Build out an estimate of all combos
        with get_sqlalchemy_conn("postgis") as conn:
            domain = pd.read_sql(
                text(
                    f"""
                select distinct phenomena || '.' || significance as key from
                warnings_{year}
                """
                ),
                conn,
                index_col="key",
            )
    else:
        domain = statdf

    combos = None
    for panel in mp.panels:
        df2 = df.to_crs(panel.crs).cx[
            slice(*panel.get_xlim()), slice(*panel.get_ylim())
        ]

        if df2.empty:
            continue
        combos = df2["ps"].unique().tolist()
    if not combos or len(mp.panels) > 1:
        combos = df["ps"].unique().tolist()
    handles = []
    labels = []
    alphas = []
    for key in domain.index.values:
        present = False
        if key in combos:
            present = True
            combos.remove(key)
        handles.append(
            Rectangle(
                (0, 0),
                1,
                1,
                fc=NWS_COLORS.get(key, "k"),
                alpha=1 if present else 0.2,
            )
        )
        label = get_ps(key)
        if "zone_pop" in statdf.columns:
            label += (
                f"\n{statdf.at[key, 'final_pop']:,.0f} ppl,"
                f" {statdf.at[key, 'final_area_sqkm']:,.0f} km$^2$"
            )
        labels.append(label)
        alphas.append(1 if present else 0.2)
    for key in combos:
        handles.append(
            Rectangle(
                (0, 0),
                1,
                1,
                fc=NWS_COLORS.get(key, "k"),
            )
        )
        labels.append(get_ps(key))
        alphas.append(1)
    legend = mp.panels[0].ax.legend(
        handles,
        labels,
        ncol=5,
        bbox_to_anchor=(-0.03, -0.02),
        loc="upper left",
        fontsize=9,
    )
    for i, txt in enumerate(legend.get_texts()):
        txt.set_alpha(alphas[i])


def plotdf(mp, df):
    """Do plotting."""
    df["color"] = df["ps"].apply(lambda x: NWS_COLORS.get(x, "k"))
    for panel in mp.panels:
        for sig in ["S", "Y", "A", "W"]:
            df2 = (
                df[df["significance"] == sig]
                .to_crs(panel.crs)
                .cx[slice(*panel.get_xlim()), slice(*panel.get_ylim())]
            )

            if df2.empty:
                continue
            df2.plot(
                ax=panel.ax,
                aspect=None,
                color=df2["color"],
                zorder=Z_OVERLAY2 + 2,
            )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    valid = ctx["valid"].replace(tzinfo=timezone.utc)
    isscol = "issue" if ctx["opt"] == "within" else "product_issue"
    with get_sqlalchemy_conn("postgis") as conn:
        ugcdf = gpd.read_postgis(
            text(
                f"""
            select w.ugc, simple_geom, phenomena, significance,
            phenomena || '.' || significance as ps,
            w.wfo || eventid || phenomena || significance as key
            from warnings w
            JOIN ugcs u on (w.gid = u.gid)
            WHERE {isscol} <= :valid and expire >= :valid
            ORDER by phenomena asc
            """
            ),
            conn,
            params={"valid": valid},
            geom_col="simple_geom",
        )
        sbwdf = gpd.read_postgis(
            text(
                """
            select geom, phenomena, significance,
            phenomena || '.' || significance as ps,
            wfo || eventid || phenomena || significance as key
            from sbw
            WHERE polygon_begin <= :valid and polygon_end > :valid
            ORDER by phenomena asc
            """
            ),
            conn,
            params={"valid": valid},
            geom_col="geom",
        )
    mp = MapPlot(
        apctx=ctx,
        nocaption=True,
        figsize=(12.00, 12.00),
        axes_position=[0.03, 0.38, 0.94, 0.54],
    )
    # Le Sigh
    mp.fig.text(
        0.1, 0.965, "NWS Watch, Warning, and Advisory Map", fontsize=20
    )
    mp.fig.text(
        0.1,
        0.94,
        (
            "Based on Unofficial IEM Archives, "
            f"Map Valid: {valid:%d %b %Y %H:%M} UTC"
        ),
        fontsize=14,
    )

    if not ugcdf.empty:
        if ctx["add"] == "stats" and valid > utc(2005, 10, 1):
            uri = (
                f"http://iem.local/plotting/auto/plot/224/opt:{ctx['opt']}::"
                f"valid:{valid:%Y-%m-%d%%20%H%M}.csv"
            )
            with httpx.Client() as client:
                res = client.get(uri, timeout=60)
                if res.status_code != 200:
                    raise ValueError("Failed to fetch data")
                sio = StringIO(res.text)
                statsdf = pd.read_csv(sio).set_index("key")
        else:
            statsdf = pd.DataFrame({"key": ugcdf["ps"].unique()}).set_index(
                "key"
            )
        make_legend(mp, ugcdf, statsdf, valid.year - 1)
        if not sbwdf.empty:
            # remove rows from ugcdf where key is in sbwdf
            ugcdf = ugcdf[~ugcdf["key"].isin(sbwdf["key"])]
        plotdf(mp, ugcdf)
        if not sbwdf.empty:
            plotsbw(mp, sbwdf)
    if ctx["sc"] == "yes":
        mp.drawcounties()
    return mp.fig


if __name__ == "__main__":
    plotter({})
