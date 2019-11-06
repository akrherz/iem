"""Create a plot of SMOS data for either 0 or 12z"""
import sys
import datetime

import numpy as np
import pytz
import matplotlib.cm as cm
from pandas.io.sql import read_sql
from pyiem.plot.geoplot import MapPlot
from pyiem.util import get_dbconn, logger

LOG = logger()


def makeplot(ts, routes="ac"):
    """
    Generate two plots for a given time GMT
    """
    pgconn = get_dbconn("smos", user="nobody")
    df = read_sql(
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
        pgconn,
        params=(
            ts - datetime.timedelta(hours=6),
            ts + datetime.timedelta(hours=6),
        ),
        index_col=None,
    )

    if df.empty:
        LOG.info(
            "Did not find SMOS data for: %s-%s",
            ts - datetime.timedelta(hours=6),
            ts + datetime.timedelta(hours=6),
        )
        return

    for sector in ["midwest", "iowa"]:
        clevs = np.arange(0, 71, 5)
        mp = MapPlot(
            sector=sector,
            axisbg="white",
            title="SMOS Satellite: Soil Moisture (0-5cm)",
            subtitle="Satelite passes around %s UTC"
            % (ts.strftime("%d %B %Y %H"),),
        )
        if sector == "iowa":
            mp.drawcounties()
        cmap = cm.get_cmap("jet_r")
        cmap.set_under("#EEEEEE")
        cmap.set_over("k")
        mp.hexbin(
            df["lon"].values,
            df["lat"].values,
            df["sm"],
            clevs,
            units="%",
            cmap=cmap,
        )
        pqstr = "plot %s %s00 smos_%s_sm%s.png smos_%s_sm%s.png png" % (
            routes,
            ts.strftime("%Y%m%d%H"),
            sector,
            ts.strftime("%H"),
            sector,
            ts.strftime("%H"),
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
            subtitle="Satelite passes around %s UTC"
            % (ts.strftime("%d %B %Y %H"),),
        )
        if sector == "iowa":
            mp.drawcounties()
        cmap = cm.get_cmap("jet")
        cmap.set_under("#EEEEEE")
        cmap.set_over("k")
        mp.hexbin(
            df["lon"].values, df["lat"].values, df["od"], clevs, cmap=cmap
        )
        pqstr = "plot %s %s00 smos_%s_od%s.png smos_%s_od%s.png png" % (
            routes,
            ts.strftime("%Y%m%d%H"),
            sector,
            ts.strftime("%H"),
            sector,
            ts.strftime("%H"),
        )
        mp.postprocess(pqstr=pqstr)
        mp.close()


def main(argv):
    """Go Main Go"""
    if len(argv) == 2:
        hr = int(argv[1])
        if hr == 12:  # Run for the previous UTC day
            ts = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ts = ts.replace(tzinfo=pytz.utc).replace(
                hour=12, minute=0, second=0, microsecond=0
            )
        else:
            ts = datetime.datetime.utcnow()
            ts = ts.replace(tzinfo=pytz.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        makeplot(ts)
        # Run a day, a week ago ago as well
        for d in [1, 5]:
            ts -= datetime.timedelta(days=d)
            makeplot(ts, "a")
    else:
        ts = datetime.datetime(
            int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])
        )
        ts = ts.replace(tzinfo=pytz.utc)
        makeplot(ts, "a")


if __name__ == "__main__":
    main(sys.argv)
