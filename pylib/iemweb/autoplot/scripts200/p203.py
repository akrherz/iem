"""
This application generates a visual summary of polygons issued for a given
UTC date.

<p>Due to the plot's oblong nature, there is no present way to control the
plot's resolution.
"""

import datetime
import os
from io import StringIO

import matplotlib.image as mpimage
import pandas as pd
from geopandas import read_postgis
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import VTEC_PHENOMENA
from pyiem.plot import figure
from pyiem.plot.util import fitbox
from pyiem.util import get_autoplot_context, utc
from sqlalchemy import text

PDICT = {
    "W": "By Issuance Center",
    "S": "By Polygon Size",
    "T": "By Issuance Time",
}
PDICT2 = {
    "W": "Tornado + Severe Thunderstorm Warnings",
    "F": "Flash Flood Warnings",
    "M": "Marine Warnings",
}
COLORS = {"SV": "#ffff00", "TO": "#ff0000", "FF": "#00ff00", "MA": "#00ff00"}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {
        "description": __doc__,
        "data": True,
        "text": True,
        "defaults": {"_r": None},
        "cache": 600,
        "plotmetadata": False,
        "gallery": {
            "date": "2024-05-05",  # pick a date with not too many
        },
    }
    today = datetime.date.today()
    desc["arguments"] = [
        dict(
            type="select",
            options=PDICT2,
            default="W",
            name="typ",
            label="Which warning types to plot?",
        ),
        dict(
            type="select",
            options=PDICT,
            default="W",
            name="sort",
            label="How to sort plotted polygons:",
        ),
        dict(
            type="date",
            default=today.strftime("%Y/%m/%d"),
            name="date",
            label="UTC Date to Plot Polygons for:",
        ),
    ]
    return desc


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    typ = ctx["typ"]
    sort = ctx["sort"]
    date = ctx["date"]

    sts = utc(date.year, date.month, date.day)
    ets = sts + datetime.timedelta(hours=24)

    opts = {
        "W": {
            "fnadd": "-wfo",
            "sortby": "wfo ASC, phenomena ASC, eventid ASC",
        },
        "S": {"fnadd": "", "sortby": "size DESC"},
        "T": {"fnadd": "-time", "sortby": "issue ASC"},
    }
    phenoms = {"W": ["TO", "SV"], "F": ["FF"], "M": ["MA"]}

    # Defaults
    thumbpx = 100
    cols = 10
    mybuffer = 10000
    header = 35

    # Find largest polygon either in height or width
    with get_sqlalchemy_conn("postgis") as conn:
        gdf = read_postgis(
            text(
                f"""
            SELECT wfo, phenomena, eventid, issue,
            ST_area2d(ST_transform(geom,9311)) as size,
            (ST_xmax(ST_transform(geom,9311)) +
            ST_xmin(ST_transform(geom,9311))) /2.0 as xc,
            (ST_ymax(ST_transform(geom,9311)) +
            ST_ymin(ST_transform(geom,9311))) /2.0 as yc,
            ST_transform(geom, 9311) as utmgeom,
            (ST_xmax(ST_transform(geom,9311)) -
            ST_xmin(ST_transform(geom,9311))) as width,
            (ST_ymax(ST_transform(geom,9311)) -
            ST_ymin(ST_transform(geom,9311))) as height
            from sbw_{sts.year}
            WHERE status = 'NEW' and issue >= :sts and issue < :ets and
            phenomena = ANY(:phenomena) and eventid is not null
            ORDER by {opts[sort]["sortby"]}
        """
            ),
            conn,
            params={"sts": sts, "ets": ets, "phenomena": phenoms[typ]},
            geom_col="utmgeom",
            index_col=None,
        )

        # For size reduction work
        df = pd.read_sql(
            text(
                f"""
            SELECT w.wfo, phenomena, eventid,
            sum(ST_area2d(ST_transform(u.geom,9311))) as county_size
            from warnings_{sts.year} w JOIN ugcs u on (u.gid = w.gid)
            WHERE issue >= :sts and issue < :ets and
            significance = 'W' and phenomena = ANY(:phenomena)
            GROUP by w.wfo, phenomena, eventid
        """
            ),
            conn,
            params={"sts": sts, "ets": ets, "phenomena": phenoms[typ]},
            index_col=["wfo", "phenomena", "eventid"],
        )
    # Join the columns
    gdf = gdf.merge(df, on=["wfo", "phenomena", "eventid"])
    gdf["ratio"] = (1.0 - (gdf["size"] / gdf["county_size"])) * 100.0

    # Make mosaic image
    events = len(df.index)
    rows = int(events / cols) + 1
    if events % cols == 0:
        rows -= 1
    if rows == 0:
        rows = 1
    ypixels = (rows * thumbpx) + header
    fig = figure(figsize=(thumbpx * cols / 100.0, ypixels / 100.0), apctx=ctx)
    fig.add_axes([0, 0, 1, 1], facecolor="black")

    imagemap = StringIO()
    utcnow = utc()
    imagemap.write(
        "<!-- %s %s -->\n" % (utcnow.strftime("%Y-%m-%d %H:%M:%S"), sort)
    )
    imagemap.write("<map name='mymap'>\n")

    # Write metadata to image
    mydir = os.sep.join(
        [
            os.path.dirname(os.path.abspath(__file__)),
            "../../../../htdocs/images",
        ]
    )
    logo = mpimage.imread(f"{mydir}/logo_reallysmall.png")
    y0 = fig.get_figheight() * 100.0 - logo.shape[0] - 5
    fig.figimage(logo, 5, y0, zorder=3)

    i = 0
    # amount of NDC y space we have for axes plotting
    ytop = 1 - header / float((rows * 100) + header)
    dy = ytop / float(rows)
    ybottom = ytop

    # Sumarize totals
    y = ytop
    dy2 = (1.0 - ytop) / 2.0
    for phenomena, df2 in gdf.groupby("phenomena"):
        car = (1.0 - df2["size"].sum() / df2["county_size"].sum()) * 100.0
        fitbox(
            fig,
            ("%i %s.W: Avg size %5.0f km^2 CAR: %.0f%%")
            % (len(df2.index), phenomena, df2["size"].mean() / 1e6, car),
            0.8,
            0.99,
            y,
            y + dy2,
            color=COLORS[phenomena],
        )
        y += dy2

    fitbox(
        fig,
        "NWS %s Storm Based Warnings issued %s UTC"
        % (
            " + ".join([VTEC_PHENOMENA[p] for p in phenoms[typ]]),
            sts.strftime("%d %b %Y"),
        ),
        0.05,
        0.79,
        ytop + dy2,
        0.999,
        color="white",
    )
    fitbox(
        fig,
        "Generated: %s UTC, IEM Autplot #203"
        % (utcnow.strftime("%d %b %Y %H:%M:%S"),),
        0.05,
        0.79,
        ytop,
        0.999 - dy2,
        color="white",
    )
    # We want to reserve 14pts at the bottom and buffer the plot by 10km
    # so we compute this in the y direction, since it limits us
    max_dimension = max([gdf["width"].max(), gdf["height"].max()])
    yspacing = max_dimension / 2.0 + mybuffer
    xspacing = yspacing * 1.08  # approx

    for _, row in gdf.iterrows():
        # - Map each polygon
        x0 = float(row["xc"]) - xspacing
        x1 = float(row["xc"]) + xspacing
        y0 = float(row["yc"]) - yspacing - (yspacing * 0.14)
        y1 = float(row["yc"]) + yspacing - (yspacing * 0.14)

        col = i % 10
        if col == 0:
            ybottom -= dy
        ax = fig.add_axes(
            [col * 0.1, ybottom, 0.1, dy],
            facecolor="black",
            xticks=[],
            yticks=[],
            aspect="auto",
        )
        for x in ax.spines:
            ax.spines[x].set_visible(False)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        for poly in row["utmgeom"].geoms:
            xs, ys = poly.exterior.xy
            color = COLORS[row["phenomena"]]
            ax.plot(xs, ys, color=color, lw=2)

        car = "NA"
        carColor = "white"
        if not pd.isnull(row["ratio"]):
            carf = row["ratio"]
            car = "%.0f" % (carf,)
            if carf > 75:
                carColor = "green"
            if carf < 25:
                carColor = "red"

        # Draw Text!
        issue = row["issue"]
        s = "%s.%s.%s.%s" % (
            row["wfo"],
            row["phenomena"],
            row["eventid"],
            issue.strftime("%H%M"),
        )
        ax.text(
            0,
            0,
            s,
            transform=ax.transAxes,
            color="white",
            va="bottom",
            fontsize=7,
        )
        s = "%.0f sq km %s%%" % (row["size"] / 1000000.0, car)
        ax.text(
            0,
            0.1,
            s,
            transform=ax.transAxes,
            color=carColor,
            va="bottom",
            fontsize=7,
        )

        # Image map
        url = ("/vtec/#%s-O-NEW-K%s-%s-%s-%04i") % (
            sts.year,
            row["wfo"],
            row["phenomena"],
            "W",
            row["eventid"],
        )
        altxt = "Click for text/image"
        pos = ax.get_position()
        mx0 = pos.x0 * 1000.0
        my = (1.0 - pos.y1) * ypixels
        imagemap.write(
            (
                '<area href="%s" alt="%s" title="%s" '
                'shape="rect" coords="%.0f,%.0f,%.0f,%.0f">\n'
            )
            % (url, altxt, altxt, mx0, my, mx0 + thumbpx, my + thumbpx)
        )
        i += 1

    faux = fig.add_axes([0, 0, 1, 1], facecolor="None", zorder=100)
    for i in range(1, rows):
        faux.axhline(i * dy, lw=1.0, color="blue")

    imagemap.write("</map>")
    imagemap.seek(0)

    if gdf.empty:
        fitbox(fig, "No warnings Found!", 0.2, 0.8, 0.2, 0.5, color="white")

    return fig, gdf.drop(columns=["utmgeom", "issue"]), imagemap.read()
