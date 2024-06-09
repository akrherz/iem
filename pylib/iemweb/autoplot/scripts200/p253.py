"""
This autoplot combines
<a href="https://apps.dat.noaa.gov/stormdamage/damageviewer/">
NWS Damage Assessment Toolkit</a> (DAT) tornado tracks
(lines) with Tornado Warning (polygons) to provide along track estimates of
lead time.  This is all unofficial, of course, and makes assumptions about
constant travel speed of the tornado along the track.  The lead time is
evaluated at 1 minute intervals and follows a method found in:
Stumpf 2024: <a
href="https://journals.ametsoc.org/view/journals/wefo/39/5/WAF-D-23-0153.1.xml">
A Geospatial Verification Method for Severe Convective Weather
Warnings: Implications for Current and Future Warning Methods</a>. Points
receiving a warning after observation are assigned a negative lead time. Points
receiving no warning are assigned a no lead time and not considered in the
lead time average.
</p>

<p>The data download option will provide the discritized points along the
tornado track with the lead time in minutes.</p>

"""

import datetime
from zoneinfo import ZoneInfo

import geopandas as gpd
import matplotlib.colors as mpcolors
import matplotlib.dates as mpdates
import numpy as np
import pandas as pd
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import rgb2hex
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MAIN_AX_BOUNDS, MapPlot
from pyiem.util import get_autoplot_context
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    return {
        "description": __doc__,
        "data": True,
        "cache": 86400,
        "gallery": {
            "dat": "2024-05-21",
            "datglobalid": "{495DE596-B299-41FE-9C90-13C87E43FE0B}",
        },
        "arguments": [
            {
                "type": "dat",
                "name": "dat",
                "default": "2024-05-21",
                "label": "Select Date + Tornado Track to plot:",
            },
            {
                "type": "cmap",
                "name": "cmap",
                "default": "gist_rainbow",
                "label": "Color Ramp:",
            },
        ],
    }


def plot_points(mp, pts):
    """Plot the discritized points."""
    pos = pts[pts["lead"] >= 0]
    if not pos.empty:
        pos.to_crs(mp.panels[0].crs).plot(
            ax=mp.panels[0].ax,
            aspect=None,
            fc=pos["color"],
            ec="k",
            zorder=11,
        )
    pos = pts[pts["lead"] < 0]
    if not pos.empty:
        pos.to_crs(mp.panels[0].crs).plot(
            ax=mp.panels[0].ax,
            aspect=None,
            c="k",
            marker="*",
            zorder=11,
        )
    pos = pts[pts["lead"].isna()]
    if not pos.empty:
        pos.to_crs(mp.panels[0].crs).plot(
            ax=mp.panels[0].ax,
            aspect=None,
            c="k",
            marker="x",
            zorder=11,
        )


def plot_tow(tow, mp, tzinfo):
    """Plot the tornado warnings."""
    tow.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        facecolor="#ff000033",
        edgecolor="#ff0000ff",
        lw=1.5,
        zorder=9,
    )
    bounds = mp.panels[0].ax.get_xlim() + mp.panels[0].ax.get_ylim()
    # status positions for label placement
    # LL, UR, UL, LR
    status = [
        (0.1, 0.1),
        (0.3, 0.9),  # legend
        (0.9, 0.9),
        (0.9, 0.1),
    ]
    for _, row in tow.to_crs(mp.panels[0].crs).iterrows():
        label = "%s Tor Warning #%s\n%s till %s" % (
            row["wfo"],
            row["eventid"],
            row["utc_issue"].astimezone(tzinfo).strftime("%-I:%M %p"),
            row["utc_expire"].astimezone(tzinfo).strftime("%-I:%M %p"),
        )
        x_frac = (row["geom"].centroid.x - bounds[0]) / (bounds[1] - bounds[0])
        y_frac = (row["geom"].centroid.y - bounds[2]) / (bounds[3] - bounds[2])
        if x_frac < 0.5 and y_frac < 0.5:  # LL
            pos = status[0]
            status[0] = (status[0][0], status[0][1] + 0.1)
        elif x_frac <= 0.5 <= y_frac:  # UL
            pos = status[1]
            status[1] = (status[1][0], status[1][1] - 0.1)
        elif x_frac > 0.5 and y_frac >= 0.5:  # UR
            pos = status[2]
            status[2] = (status[2][0], status[2][1] - 0.1)
        else:
            pos = status[3]
            status[3] = (status[3][0], status[3][1] + 0.1)
        mp.panels[0].ax.annotate(
            label,
            xy=(max(min(0.98, x_frac), 0.02), max(min(0.98, y_frac), 0.02)),
            xytext=pos,
            xycoords="axes fraction",
            textcoords="axes fraction",
            arrowprops=dict(facecolor="black", shrink=0.05, width=2),
            bbox=dict(color="#f1bebe", boxstyle="round,pad=0.1"),
            ha="center",
            color="k",
            zorder=12,
        )


def plot_timeseries(mp, pts, tzinfo):
    """Show a time profile of the lead time."""
    ax = mp.fig.add_axes([0.4, 0.06, 0.35, 0.13])
    ax.plot(pts["valid"], pts["lead"], lw=2, color="k", zorder=1)
    ax.scatter(pts["valid"], pts["lead"], c=pts["color"], zorder=2)
    ax.set_xlim(pts["valid"].min(), pts["valid"].max())
    ax.set_yticks(range(0, 61, 15))
    ax.xaxis.set_major_formatter(
        mpdates.DateFormatter("%-I:%M\n%p", tz=tzinfo)
    )
    ax.grid(True)
    ax.text(
        0.01,
        1.01,
        f"Lead Time Profile (minutes) [min: {pts['lead'].min():.0f} "
        f"max: {pts['lead'].max():.0f}]",
        transform=ax.transAxes,
        va="bottom",
        ha="left",
        bbox=dict(facecolor="white", edgecolor="tan", pad=1),
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    # Eh
    datglobalid = fdict.get("datglobalid")
    if datglobalid is None or datglobalid == "":
        raise NoDataFound("No DAT globalid provided...")

    nt = NetworkTable("WFO")
    tzinfo = ZoneInfo("America/Chicago")

    # Get the track
    trackgdf = gpd.read_file(
        "https://services.dat.noaa.gov/arcgis/rest/services/"
        "nws_damageassessmenttoolkit/DamageViewer/FeatureServer/1/query?"
        f"where=globalid%3D%27%7B{datglobalid[1:-1]}%7D%27&"
        "geometryType=esriGeometryPolyline&outFields=*&"
        "returnGeometry=true&f=geojson"
    )
    if len(trackgdf.index) != 1:
        raise NoDataFound("No track found for globalid provided, ask IEM...")
    wfo = trackgdf.iloc[0]["wfo"]
    if wfo is not None and len(wfo) >= 3:
        tzinfo = ZoneInfo(nt.sts[wfo[:3]]["tzname"])
    # convert the starttime (java ticks) to a UTC datetime
    for col in ["starttime", "endtime"]:
        trackgdf[col] = pd.to_datetime(
            trackgdf[col] / 1000,
            unit="s",
        ).dt.tz_localize(datetime.timezone.utc)
    track_sts = trackgdf.iloc[0]["starttime"]
    track_ets = trackgdf.iloc[0]["endtime"]
    # Get the warning polygons
    with get_sqlalchemy_conn("postgis") as conn:
        tow = gpd.read_postgis(
            text(
                """
            SELECT wfo, eventid, phenomena, significance,
            issue at time zone 'UTC' as utc_issue,
            expire at time zone 'UTC' as utc_expire,
            geom from sbw WHERE vtec_year = :year and phenomena = 'TO' and
            significance = 'W'
            and status = 'NEW' and issue <= :ets and expire >= :sts and
            ST_Intersects(geom, ST_SetSRID(ST_GeomFromEWKT(:geom), 4326))
            ORDER by utc_issue ASC
            """
            ),
            conn,
            params={
                "year": trackgdf.iloc[0]["starttime"].year,
                "sts": track_sts,
                "ets": track_ets,
                "geom": trackgdf.iloc[0]["geometry"].wkt,
            },
            geom_col="geom",
        )
    if not tow.empty:
        for col in ["utc_issue", "utc_expire"]:
            tow[col] = tow[col].dt.tz_localize(datetime.timezone.utc)

    minutes = int((track_ets - track_sts).total_seconds() / 60.0)
    if minutes <= 0:
        raise NoDataFound("Tornado track has no time duration in DAT!")
    # Do work in US Albers
    utm_track = trackgdf.to_crs(epsg=2163).geometry[0]
    speed = utm_track.length / minutes * 60.0  # km/hr
    speed_mph = speed * 0.621371 / 1000.0
    rows = []
    for minute in range(minutes + 1):
        # Compute the time of the segment
        valid = track_sts + datetime.timedelta(minutes=minute)
        # Compute the distance of the segment
        pt = utm_track.interpolate(minute / minutes * utm_track.length)
        rows.append({"geom": pt, "valid": valid})
    cmap = get_cmap(ctx["cmap"])
    if cmap.N < 13:
        bins = list(range(0, 61, 10))
    else:
        bins = list(range(0, 61, 5))
    norm = mpcolors.BoundaryNorm(bins, cmap.N)

    pts = gpd.GeoDataFrame(
        rows, columns=["geom", "valid"], geometry="geom", crs="EPSG:2163"
    ).to_crs("EPSG:4326")
    pts["lat"] = pts["geom"].y
    pts["lon"] = pts["geom"].x
    pts["lead"] = np.nan
    for idx, row in pts.iterrows():
        valid = row["valid"]
        # Find candidate warnings, these are sorted by issue time, so the
        # first one is the one we care about
        ol = tow[tow.intersects(row.geom)]
        if ol.empty:
            continue
        # Find ones that overlap in time first
        dol = ol[(ol["utc_issue"] <= valid) & (ol["utc_expire"] >= valid)]
        if not dol.empty:
            pts.at[idx, "lead"] = (
                valid - dol.iloc[0].utc_issue
            ).total_seconds() / 60.0
            continue
        # Look for the next warning after this time
        dol = ol[ol["utc_issue"] > valid]
        if not dol.empty:
            pts.at[idx, "lead"] = (
                valid - dol.iloc[0].utc_issue
            ).total_seconds() / 60.0
    pts["color"] = pts["lead"].apply(
        lambda x: rgb2hex(cmap(norm(x))) if x >= 0 else "#000000"
    )
    stats = pts["lead"].describe()
    bounds = trackgdf.total_bounds

    buffer = 0.01
    label = trackgdf.iloc[0]["event_id"]
    if label is None or label == "":
        label = (
            f"Unlabeled Tornado from {trackgdf.iloc[0]['wfo']} on "
            f"{track_sts.astimezone(tzinfo).strftime('%-d %b %Y')}"
        )
    ef = trackgdf.iloc[0]["efscale"]
    if ef is None:
        ef = ""
    mp = MapPlot(
        apctx=ctx,
        continental_color="white",
        nocaption=True,
        sector="spherical_mercator",
        title=("Estimated Tornado Warning Lead Time Along Tornado Track"),
        subtitle=(
            f"{ef} {label}. "
            f"Assuming constant {speed_mph:.0f} MPH movement, "
            f"Average Lead Time: {stats['mean']:.0f} minutes"
        ),
        west=bounds[0] - buffer,
        east=bounds[2] + buffer,
        south=bounds[1] - buffer,
        north=bounds[3] + buffer,
        axes_position=[
            MAIN_AX_BOUNDS[0],
            MAIN_AX_BOUNDS[1] + 0.15,
            MAIN_AX_BOUNDS[2],
            MAIN_AX_BOUNDS[3] - 0.15,
        ],
    )
    plot_timeseries(mp, pts, tzinfo)

    trackgdf.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        lw=2,
        alpha=0.2,
        color="k",
        zorder=10,
    )
    plot_points(mp, pts)

    mp.panels[0].ax.text(
        0.01,
        -0.02,
        (
            f"Start: {track_sts.astimezone(tzinfo).strftime('%-I:%M %p %Z')}\n"
            f"End: {track_ets.astimezone(tzinfo).strftime('%-I:%M %p %Z')}\n"
            f"Duration: {minutes} minutes\n"
        ),
        va="top",
        transform=mp.panels[0].ax.transAxes,
        ha="left",
    )
    if not tow.empty:
        plot_tow(tow, mp, tzinfo)
    # Draw a color bar
    ncb = ColorbarBase(
        mp.cax,
        norm=norm,
        cmap=cmap,
        extend="neither",
        spacing="uniform",
    )
    ncb.ax.tick_params(labelsize=8)
    ncb.set_label(
        "Lead Time (minutes)",
    )
    # Create a legend for the warnings
    lng = mp.panels[0].ax.legend(
        [
            Rectangle((0, 0), 1, 1, ec="r", fc="r", alpha=0.2),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="r",
                markersize=10,
            ),
            Line2D([0], [0], marker="x", color="k", linestyle="None"),
            Line2D([0], [0], marker="*", color="k", linestyle="None"),
        ],
        [
            "Tornado Warning",
            "Positive Lead Time",
            "No Lead Time",
            "Negative Lead Time",
        ],
        loc=2,
        framealpha=1,
    )
    lng.set_zorder(12)

    return mp.fig, pts.drop(columns=["geom"])
