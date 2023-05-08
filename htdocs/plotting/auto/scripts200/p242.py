"""
Presently, this autoplot is a backend for generating Local Storm Report
social media graphics.  You have to know the associated NWS text product
id for it to be of any usage. Perhaps this autoplot will become more useful
in the future for interactive use!
"""
from textwrap import wrap

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # noqa

import geopandas as gpd
import matplotlib.patheffects as PathEffects
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot, plt
from pyiem.plot.geoplot import MAIN_AX_BOUNDS
from pyiem.reference import Z_OVERLAY2
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text

ICONS = {
    "0": "tropicalstorm.gif",
    "1": "flood.png",
    "2": "other.png",
    "3": "other.png",
    "4": "other.png",
    "5": "ice.png",
    "6": "cold.png",
    "7": "cold.png",
    "8": "fire.png",
    "9": "other.png",
    "a": "other.png",
    "A": "wind.png",
    "B": "downburst.png",
    "C": "funnelcloud.png",
    "D": "winddamage.png",
    "E": "flood.png",
    "F": "flood.png",
    "v": "flood.png",
    "G": "wind.png",
    "H": "hail.png",
    "I": "hot.png",
    "J": "fog.png",
    "K": "lightning.gif",
    "L": "lightning.gif",
    "M": "wind.png",
    "N": "wind.png",
    "O": "wind.png",
    "P": "other.png",
    "Q": "tropicalstorm.gif",
    "s": "sleet.png",
    "T": "tornado.png",
    "U": "fire.png",
    "V": "avalanche.gif",
    "W": "waterspout.png",
    "X": "funnelcloud.png",
    "x": "debrisflow.png",
    "Z": "blizzard.png",
}
PE = [PathEffects.withStroke(linewidth=5, foreground="white")]


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    desc["arguments"] = [
        {
            "type": "text",
            "default": "202305080216-KDMX-NWUS53-LSRDMX",
            "name": "pid",
            "label": "Enter NWS Text Product Identifier",
        },
    ]
    return desc


def get_image(filename):
    """Get an image"""
    fn = f"/opt/iem/htdocs/lsr/icons/{filename}"
    return OffsetImage(plt.imread(fn, format="png"), zoom=0.7)


def overlay_info(fig, df):
    """Add bling."""
    if len(df.index) > 1:
        msg = ""
        lines = 0
        xpos = 0.5
        for typetext, gdf in df.groupby("typetext"):
            msg += f"_____ {typetext} _____\n"
            for _, row in gdf.iterrows():
                if lines > 30:
                    fig.text(
                        xpos,
                        0.9,
                        msg,
                        bbox=dict(fc="white", ec="k"),
                        va="top",
                        fontsize=10,
                    )
                    msg = f"_____ {typetext} _____\n"
                    xpos += 0.2
                    lines = 1
                msg += f"{row['city']} {row['magnitude']}\n"
                lines += 1
        fig.text(
            xpos,
            0.9,
            msg,
            bbox=dict(fc="white", ec="k"),
            va="top",
            fontsize=10,
        )
        return
    row = df.iloc[0]
    remark = ""
    if row["remark"] is not None:
        remark = "\n".join(wrap(row["remark"].strip(), width=50))
    msg = (
        f"Valid: {row['utc_valid']:%Y-%m-%d %H:%M} UTC\n"
        f"Local Valid: {row['local_valid']:%Y-%m-%d %-I:%M %p}\n"
        f"Location: {row['city']} [{row['county']}], {row['state']}\n"
        f"Source: {row['source']}\n"
        f"Event: {row['typetext']} {row['magnitude']} {row['unit']}\n"
        f"Remark: {remark}"
    )
    fig.text(
        0.5,
        0.85,
        msg,
        bbox=dict(fc="white", ec="k"),
        va="top",
    )


def get_df(table, product_id):
    """Find me data."""
    with get_sqlalchemy_conn("postgis") as conn:
        df = gpd.read_postgis(
            text(
                f"""
            SELECT *, null as local_valid,
            valid at time zone 'UTC' as utc_valid
            from {table} WHERE (product_id = :pid or product_id_summary = :pid)
            ORDER by magnitude DESC NULLS LAST
            """
            ),
            conn,
            params={"pid": product_id},
            geom_col="geom",
            parse_dates=[
                "utc_valid",
            ],
        )
    if not df.empty:
        df["utc_valid"] = df["utc_valid"].dt.tz_localize(ZoneInfo("UTC"))
        nt = NetworkTable("WFO")
        wfo = product_id[14:17]
        if wfo in nt.sts:
            tzinfo = ZoneInfo(nt.sts[wfo]["tzname"])
            df["local_valid"] = df["utc_valid"].dt.tz_convert(tzinfo)
    return df


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    product_id = ctx["pid"]
    # Can we find data?
    df = get_df(f"lsrs_{product_id[:4]}", product_id)
    if df.empty:
        df = get_df("lsrs", product_id)
    if df.empty:
        raise NoDataFound("Failed to find LSRs by given product identifier!")
    df["magnitude"] = df["magnitude"].fillna("")
    if len(df.index) == 1:
        title = f"LSR: {df.at[0, 'city']} {df.at[0, 'typetext']}"
        timeinfo = f"@ {df.at[0, 'local_valid']:%-d %b %Y %-I:%M %p}"
        pos = MAIN_AX_BOUNDS
    else:
        title = "Local Storm Reports"
        mindt = df["local_valid"].min()
        maxdt = df["local_valid"].max()
        d1 = f"{mindt:%-d %b %Y %-I:%M %p}"
        d2 = f"{maxdt:%-d %b %Y %-I:%M %p}"
        if mindt.date() == maxdt.date():
            d2 = f"{maxdt:%-I:%M %p}"
        timeinfo = f"between {d1} and {d2}"
        pos = [0.01, 0.05, 0.5, 0.85]

    bounds = df["geom"].total_bounds
    buffer = 0.2 if (bounds[3] - bounds[1]) < 0.2 else 0

    # Bias to the east, for overlay
    mp = MapPlot(
        title=f"NWS {product_id[14:17]} {title} {timeinfo}",
        subtitle=f"LSRs found in product_id: {product_id}",
        apctx=ctx,
        sector="spherical_mercator",
        west=bounds[0] - buffer,
        south=bounds[1] - buffer,
        east=bounds[2] + buffer,
        north=bounds[3] + buffer,
        nocaption=True,
        axes_position=pos,
    )
    for typ, gdf in df.to_crs(mp.panels[0].crs).groupby("type"):
        if typ in ["R", "S"]:
            for _, row in gdf.iloc[::-1].iterrows():
                mp.panels[0].ax.text(
                    row["geom"].x,
                    row["geom"].y,
                    row["magnitude"],
                    color="k",
                    zorder=Z_OVERLAY2 + 1,
                ).set_path_effects(PE)
            continue
        pngfn = ICONS.get(typ)
        if pngfn is None:
            mp.panels[0].ax.scatter(
                gdf["geom"].x,
                gdf["geom"].y,
                marker="o",
                s=300,
                zorder=Z_OVERLAY2,
            )
            continue
        img = get_image(pngfn)
        for _, row in gdf.iterrows():
            ab = AnnotationBbox(
                img,
                (row["geom"].x, row["geom"].y),
                frameon=False,
                zorder=Z_OVERLAY2,
            )
            mp.panels[0].ax.add_artist(ab)

    mp.draw_cwas(linewidth=2)
    overlay_info(mp.fig, df)

    return mp.fig, df


if __name__ == "__main__":
    plotter({"pid": "202305080420-KILX-NWUS53-LSRILX"})
