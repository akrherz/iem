"""
This visualization mashes up the US Drought Monitor and three trailing
day standardized precipitation index of your choice within a map
presentation for a single state.  SPI is computed by the simple formula
of <code>(accum - climatology) / standard deviation</code>.</p>

<p>This autoplot is extremely slow to generate due to the on-the-fly
calculation of standard deviation. As such, an optimization is done to
sub-sample from available stations since the resulting map can only display
a certain number of data points legibly. This means that the dataset you
download from this page does not contain all available stations for a given
state :/
"""

import sys
from datetime import date, timedelta

import geopandas as gpd
import matplotlib.colors as mpcolors
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import NoDataFound
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY2, state_bounds
from pyiem.util import get_autoplot_context
from sqlalchemy import text
from tqdm import tqdm

PDICT = {
    "normal": "Normal Mode / Plot by State",
    "iadrought": "Special Iowa Drought Monitoring",
}


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {"description": __doc__, "data": True}
    dt = date.today() - timedelta(days=1)
    desc["arguments"] = [
        {
            "type": "select",
            "name": "mode",
            "default": "normal",
            "label": "Application Mode:",
            "options": PDICT,
        },
        dict(
            type="state",
            name="state",
            default="IA",
            label="Select State:",
        ),
        dict(
            type="date",
            name="date",
            default=dt.strftime("%Y/%m/%d"),
            label="Retroactive Date of Plot",
        ),
        dict(
            type="int",
            name="d1",
            default=30,
            label="Over how many trailing days to compute the metric?",
        ),
        dict(
            type="int",
            name="d2",
            default=60,
            label="Over how many trailing days to compute the metric?",
        ),
        dict(
            type="int",
            name="d3",
            default=90,
            label="Over how many trailing days to compute the metric?",
        ),
    ]
    return desc


def overlay_drought_regions(mp):
    """Add an overlay."""
    with get_sqlalchemy_conn("coop") as conn:
        gdf = gpd.read_postgis(
            """
            SELECT id, c.geom from climodat_regions c JOIN stations t on
            (c.iemid = t.iemid) WHERE t.network = 'IACLIMATE' and
            substr(id, 3, 1) = 'D'
            """,
            conn,
            index_col="id",
            geom_col="geom",
        )
    if gdf.empty:
        return
    gdf.to_crs(mp.panels[0].crs).plot(
        ax=mp.panels[0].ax,
        aspect=None,
        lw=3,
        ec="k",
        fc="None",
        zorder=Z_OVERLAY2,
    )


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"]
    d1 = ctx["d1"]
    d2 = ctx["d2"]
    d3 = ctx["d3"]
    dt = ctx["date"]
    params = {
        "d1": d1 - 1,
        "d2": d2 - 1,
        "d3": d3 - 1,
        "date": dt,
        "sday": dt.strftime("%m%d"),
        "network": f"{state}CLIMATE",
    }
    dfs = []
    nt = NetworkTable(f"{state}CLIMATE")
    [xmin, ymin, xmax, ymax] = state_bounds[state]
    GZ = 0.5
    hits = np.zeros((int((ymax - ymin) / GZ) + 1, int((xmax - xmin) / GZ) + 1))
    with get_sqlalchemy_conn("coop") as conn:
        # A single shot query was taking moons to complete, so a brute force
        # looper seems to be net faster.  We can also cull what gets
        # processed
        progress = tqdm(nt.sts.items(), disable=not sys.stdout.isatty())
        for station, meta in progress:
            if not meta["online"]:
                continue
            if ctx["mode"] == "iadrought":
                if station[2] != "D":
                    continue
            else:
                if station[2] in ["C", "D"] or station[2:] == "0000":
                    continue
            yidx = int((meta["lat"] - ymin) / GZ)
            xidx = int((meta["lon"] - xmin) / GZ)
            hits[yidx, xidx] += 1
            if hits[yidx, xidx] > 1:
                continue
            progress.set_description(station)
            params["station"] = station
            params["lat"] = meta["lat"]
            params["lon"] = meta["lon"]
            dfs.append(
                pd.read_sql(
                    text(
                        f"""
                WITH data as (
                    SELECT sday, day,
                    sum(precip) OVER (PARTITION by station ORDER by day ASC
                    ROWS BETWEEN :d1 PRECEDING AND CURRENT ROW) as p1,
                    sum(precip) OVER (PARTITION by station ORDER by day ASC
                    ROWS BETWEEN :d2 PRECEDING AND CURRENT ROW) as p2,
                    sum(precip) OVER (PARTITION by station ORDER by day ASC
                    ROWS BETWEEN :d3 PRECEDING AND CURRENT ROW) as p3
                    from alldata_{state} WHERE day <= :date and
                    station = :station
                ), stats as (
                    SELECT avg(p1) as avg_p1, stddev(p1) as stddev_p1,
                    avg(p2) as avg_p2, stddev(p2) as stddev_p2,
                    avg(p3) as avg_p3, stddev(p3) as stddev_p3,
                    count(*)
                    from data WHERE sday = :sday
                )
                select s.avg_p1, s.stddev_p1, s.avg_p2, s.stddev_p2,
                s.avg_p3, s.stddev_p3, d.p1, d.p2, d.p3,
                (d.p1 - s.avg_p1) / s.stddev_p1 as z1,
                (d.p2 - s.avg_p2) / s.stddev_p2 as z2,
                (d.p3 - s.avg_p3) / s.stddev_p3 as z3, s.count,
                :station as station, :lat as lat, :lon as lon
                from data d, stats s WHERE d.day = :date
            """
                    ),
                    conn,
                    params=params,
                )
            )
    if not dfs:
        raise NoDataFound("Did not find any data.")
    df = pd.concat(dfs)
    # Lame roundabout for CI testing
    if len(df.index) > 10:
        df = df[df["count"] >= 30]
    if df.empty:
        raise NoDataFound("Did not find any data after filter.")
    df = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"], crs="EPSG:4326")
    )
    st = "stations w/ 30+ years of data"
    if ctx["mode"] == "iadrought":
        st = "Iowa Drought Monitoring Regions"
    mp = MapPlot(
        title="Trailing Day Standardized Precipitation Index",
        subtitle=f"Ending {dt:%B %-d %Y} computed for {st}",
        sector="state",
        state=state,
        stateborderwidth=2,
    )
    mp.draw_usdm(dt, alpha=1)
    mp.drawcounties()
    levels = [-100, -2, -1.6, -1.3, -0.8, -0.5, 0.5, 0.8, 1.3, 1.6, 2, 100]
    cmap = mpcolors.ListedColormap(
        "#730000 #e60000 #ffaa00 #fcd37f #ffff00 #ffffff "
        "#b2ff00 #00b400 #008080 #0000ff #9600ff".split()
    )
    norm = mpcolors.BoundaryNorm(levels, cmap.N)
    df = df.assign(
        color1=list(cmap(norm(df.z1))),
        color2=list(cmap(norm(df.z2))),
        color3=list(cmap(norm(df.z3))),
    )
    # Get the extent of the map
    (x0, x1, y0, y1) = mp.panels[0].get_extent()
    # Compute an offset
    xoff = (x1 - x0) * 0.0075
    yoff = (y1 - y0) * 0.0125
    markersize = 60
    if ctx["mode"] == "iadrought":
        markersize = 180
        xoff *= 2
        yoff *= 2
    df.to_crs(mp.panels[0].crs).plot(
        facecolor=df["color1"],
        edgecolor="#ffffff",
        aspect=None,
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2 + 3,
        markersize=markersize,
    )
    df.to_crs(mp.panels[0].crs).assign(
        geometry=lambda x: x.geometry.translate(xoff, -yoff)
    ).plot(
        facecolor=df["color2"],
        edgecolor="#ffffff",
        aspect=None,
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2 + 3,
        markersize=markersize,
    )
    df.to_crs(mp.panels[0].crs).assign(
        geometry=lambda x: x.geometry.translate(-xoff, -yoff)
    ).plot(
        facecolor=df["color3"],
        edgecolor="#ffffff",
        aspect=None,
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2 + 3,
        markersize=markersize,
    )
    if ctx["mode"] == "iadrought":
        overlay_drought_regions(mp)

    # Add the legend
    mp.fig.text(0.85, 0.95, "Trailing Days\nDot Legend", ha="right")
    boxs = {"boxstyle": "circle", "edgecolor": "k", "facecolor": "w"}
    mp.fig.text(0.88, 0.97, f"{d1:3.0f}", bbox=boxs)
    mp.fig.text(0.90, 0.93, f"{d2:3.0f}", bbox=boxs)
    mp.fig.text(0.86, 0.93, f"{d3:3.0f}", bbox=boxs)

    clevlabels = ["", "D4", "D3", "D2", "D1", "D0"]
    clevlabels.extend(["W0", "W1", "W2", "W3", "W4", ""])
    mp.draw_colorbar(
        levels,
        cmap,
        norm,
        extend="neither",
        clevlabels=clevlabels,
    )

    return mp.fig, df.drop(columns=["geometry"])
