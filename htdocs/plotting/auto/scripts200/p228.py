"""3 Dot Scatter plot.."""
import datetime

import geopandas as gpd
import matplotlib.colors as mpcolors
from pyiem.exceptions import NoDataFound
from pyiem.plot import MapPlot
from pyiem.reference import Z_OVERLAY2
from pyiem.util import get_autoplot_context, get_sqlalchemy_conn
from sqlalchemy import text


def get_description():
    """Return a dict describing how to call this plotter"""
    desc = {}
    desc["data"] = True
    desc[
        "description"
    ] = """
    This visualization mashes up the US Drought Monitor and three trailing
    day standardized precipitation index of your choice within a map
    presentation for a single state.  SPI is computed by the simple formula
    of <code>(accum - climatology) / standard deviation</code>.</p>

    <p>This autoplot is extremely slow to generate due to the on-the-fly
    calculation of standard deviation.  Hopefully that can be speed up
    sometime in the future!
    """
    dt = datetime.date.today() - datetime.timedelta(days=1)
    desc["arguments"] = [
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


def plotter(fdict):
    """Go"""
    ctx = get_autoplot_context(fdict, get_description())
    state = ctx["state"]
    d1 = ctx["d1"]
    d2 = ctx["d2"]
    d3 = ctx["d3"]
    date = ctx["date"]
    params = {
        "d1": d1 - 1,
        "d2": d2 - 1,
        "d3": d3 - 1,
        "date": date,
        "sday": date.strftime("%m%d"),
        "network": f"{state}CLIMATE",
        "sts": date - datetime.timedelta(days=366 * 31),
    }
    with get_sqlalchemy_conn("coop") as conn:
        df = gpd.read_postgis(
            text(
                f"""
            WITH data as (
                SELECT station, sday, day,
                sum(precip) OVER (PARTITION by station ORDER by day ASC
                ROWS BETWEEN :d1 PRECEDING AND CURRENT ROW) as p1,
                sum(precip) OVER (PARTITION by station ORDER by day ASC
                ROWS BETWEEN :d2 PRECEDING AND CURRENT ROW) as p2,
                sum(precip) OVER (PARTITION by station ORDER by day ASC
                ROWS BETWEEN :d3 PRECEDING AND CURRENT ROW) as p3
                from alldata_{state} WHERE
                day > :sts and day <= :date and
                substr(station, 3, 1) not in ('C', 'T') and
                substr(station, 3, 4) != '0000'
            ), stats as (
                SELECT station,
                avg(p1) as avg_p1, stddev(p1) as stddev_p1,
                avg(p2) as avg_p2, stddev(p2) as stddev_p2,
                avg(p3) as avg_p3, stddev(p3) as stddev_p3,
                count(*)
                from data WHERE sday = :sday GROUP by station
            ), agg as (
                select d.station, s.avg_p1, s.stddev_p1, s.avg_p2, s.stddev_p2,
                s.avg_p3, s.stddev_p3, d.p1, d.p2, d.p3,
                (d.p1 - s.avg_p1) / s.stddev_p1 as z1,
                (d.p2 - s.avg_p2) / s.stddev_p2 as z2,
                (d.p3 - s.avg_p3) / s.stddev_p3 as z3
                from data d JOIN stats s on (d.station = s.station)
                WHERE d.day = :date and s.count > 29
            )
            select a.*, geom
            from agg a JOIN stations t on (a.station = t.id)
            WHERE t.network = :network
        """
            ),
            conn,
            params=params,
            geom_col="geom",
            index_col="station",
        )
    if df.empty:
        raise NoDataFound("Did not find any data.")
    mp = MapPlot(
        title="Trailing Day Standardized Precipitation Index",
        subtitle=(
            f"Ending {date:%B %-d %Y} computed over past 30 years, "
            "expressed in Drought Classification"
        ),
        sector="state",
        state=state,
    )
    mp.draw_usdm(date, alpha=1)
    mp.drawcounties()
    levels = [-100, -2, -1.6, -1.3, -0.8, -0.5, 0.5, 0.8, 1.3, 1.6, 2, 100]
    cmap = mpcolors.ListedColormap(
        "#730000 #e60000 #ffaa00 #fcd37f #ffff00 #ffffff "
        "#b2ff00 #00b400 #008080 #0000ff #9600ff".split()
    )
    norm = mpcolors.BoundaryNorm(levels, cmap.N)
    df = df.assign(
        color1=lambda x: [a for a in cmap(norm(x.z1))],
        color2=lambda x: [a for a in cmap(norm(x.z2))],
        color3=lambda x: [a for a in cmap(norm(x.z3))],
    )
    # Get the extent of the map
    (x0, x1, y0, y1) = mp.panels[0].get_extent()
    # Compute an offset
    xoff = (x1 - x0) * 0.0075
    yoff = (y1 - y0) * 0.0125

    df.to_crs(mp.panels[0].crs).plot(
        facecolor=df["color1"],
        edgecolor="#ffffff",
        aspect=None,
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2 + 3,
        markersize=60,
    )
    df.to_crs(mp.panels[0].crs).assign(
        geom=lambda x: x.geom.translate(xoff, -yoff)
    ).plot(
        facecolor=df["color2"],
        edgecolor="#ffffff",
        aspect=None,
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2 + 3,
        markersize=60,
    )
    df.to_crs(mp.panels[0].crs).assign(
        geom=lambda x: x.geom.translate(-xoff, -yoff)
    ).plot(
        facecolor=df["color3"],
        edgecolor="#ffffff",
        aspect=None,
        ax=mp.panels[0].ax,
        zorder=Z_OVERLAY2 + 3,
        markersize=60,
    )

    # Add the legend
    mp.fig.text(0.85, 0.95, "Trailing Days\nDot Legend", ha="right")
    boxs = {"boxstyle": "circle", "edgecolor": "k", "facecolor": "w"}
    mp.fig.text(0.88, 0.97, f"{d1:3.0f}", bbox=boxs)
    mp.fig.text(0.90, 0.93, f"{d2:3.0f}", bbox=boxs)
    mp.fig.text(0.86, 0.93, f"{d3:3.0f}", bbox=boxs)

    clevlabels = "- D4 D3 D2 D1 D0 W0 W1 W2 W3 W4 -".split()
    clevlabels[0] = ""
    clevlabels[-1] = ""
    mp.draw_colorbar(
        levels,
        cmap,
        norm,
        extend="neither",
        clevlabels=clevlabels,
    )

    return mp.fig, df


if __name__ == "__main__":
    plotter({"var": "spi"})
