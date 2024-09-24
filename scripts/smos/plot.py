"""Create a plot of SMOS data for either 0 or 12z

called from RUN_NOON.sh for 0z and RUN_MIDNIGHT.sh for 12z
"""

import warnings
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import get_cmap
from pyiem.plot.geoplot import MapPlot
from pyiem.util import logger

# Surpress warning from matplotlib that I have no idea about
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()


def makeplot(ts, routes="ac"):
    """
    Generate two plots for a given time GMT
    """
    with get_sqlalchemy_conn("smos") as conn:
        df = pd.read_sql(
            """
        WITH obs as (
            SELECT grid_idx, avg(soil_moisture) * 100. as sm,
            avg(optical_depth) as od from data where valid BETWEEN %s and %s
            GROUP by grid_idx)

        SELECT ST_x(geom) as lon, ST_y(geom) as lat,
        CASE WHEN sm is Null THEN -1 ELSE sm END as sm,
        CASE WHEN od is Null THEN -1 ELSE od END as od
        from obs o JOIN grid g ON (o.grid_idx = g.idx)
        """,
            conn,
            params=(
                ts - timedelta(hours=6),
                ts + timedelta(hours=6),
            ),
            index_col=None,
        )
    if df.empty:
        LOG.warning(
            "Did not find SMOS data for: %s-%s",
            ts - timedelta(hours=6),
            ts + timedelta(hours=6),
        )
        return
    for sector in ["midwest", "iowa"]:
        clevs = np.arange(0, 71, 5)
        mp = MapPlot(
            sector=sector,
            axisbg="white",
            title="SMOS Satellite: Soil Moisture (0-5cm)",
            subtitle=f"Satelite passes around {ts:%d %B %Y %H} UTC",
        )
        if sector == "iowa":
            mp.drawcounties()
        cmap = get_cmap("jet_r")
        cmap.set_under("#EEEEEE")
        cmap.set_over("k")
        mp.hexbin(
            df["lon"].values,
            df["lat"].values,
            df["sm"].values,
            clevs,
            units="%",
            cmap=cmap,
        )
        pqstr = (
            f"plot {routes} {ts:%Y%m%d%H}00 smos_{sector}_sm{ts:%H}.png "
            f"smos_{sector}_sm{ts:%H}.png png"
        )
        mp.postprocess(pqstr=pqstr)
        mp.close()

    for sector in ["midwest", "iowa"]:
        clevs = np.arange(0, 1.001, 0.05)
        mp = MapPlot(
            sector=sector,
            axisbg="white",
            title=(
                "SMOS Satellite: Land Cover Optical Depth "
                "(microwave L-band)"
            ),
            subtitle=f"Satelite passes around {ts:%d %B %Y %H} UTC",
        )
        if sector == "iowa":
            mp.drawcounties()
        cmap = get_cmap("jet")
        cmap.set_under("#EEEEEE")
        cmap.set_over("k")
        mp.hexbin(
            df["lon"].values, df["lat"].values, df["od"], clevs, cmap=cmap
        )
        pqstr = (
            f"plot {routes} {ts:%Y%m%d%H}00 smos_{sector}_od{ts:%H}.png "
            f"smos_{sector}_od{ts:%H}.png png"
        )
        mp.postprocess(pqstr=pqstr)
        mp.close()


@click.command()
@click.option("--valid", type=click.DateTime(), help="Specific UTC time")
@click.option("--realtime", is_flag=True, help="Operate in realtime mode")
def main(valid: datetime, realtime: bool):
    """Go Main Go"""
    valid = valid.replace(tzinfo=timezone.utc)
    makeplot(valid, "ac" if realtime else "a")
    if realtime:
        for d in [1, 5]:
            makeplot(valid - timedelta(days=d), "a")


if __name__ == "__main__":
    main()
