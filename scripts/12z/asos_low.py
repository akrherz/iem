"""Generate a map of the 12z UTC low temperature.

run from RUN_SUMMARY.sh
"""

import pandas as pd
from pyiem.plot import MapPlot
from pyiem.util import get_sqlalchemy_conn, logger, utc
from sqlalchemy import text

LOG = logger()


def main():
    """Go Main Go"""
    now = utc().replace(hour=0, minute=0, second=0, microsecond=0)

    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
                """
        WITH lows as (
        SELECT c.iemid,
        min(tmpf) as calc_low,
        min(min_tmpf_6hr) as reported_low
        from current_log c JOIN stations s
        ON (s.iemid = c.iemid)
        WHERE valid > :sts and valid < :ets
        and s.network ~* 'ASOS'
        and s.country = 'US' and s.state not in ('HI', 'AK') GROUP by c.iemid
        )

        select t.id, t.state, ST_x(t.geom) as lon, ST_y(t.geom) as lat,
        least(l.calc_low, l.reported_low) as low from
        lows l JOIN stations t on (t.iemid = l.iemid)
        """
            ),
            conn,
            params={"sts": now, "ets": now.replace(hour=12)},
            index_col="id",
        )
    df = df[df["low"].notnull()]
    LOG.info("found %s observations for %s", len(df.index), now)

    for sector in [
        "iowa",
        "midwest",
        "conus",
        "SD",
        "NE",
        "ND",
        "KS",
        "MN",
        "MO",
        "WI",
        "IL",
    ]:
        mp = MapPlot(
            sector=sector if len(sector) > 2 else "state",
            state=sector if len(sector) == 2 else "IA",
            title=f"{now:%-d %b %Y} ASOS 01-12 UTC Low Temperature",
            subtitle=(
                "includes available 6z and 12z 6-hr mins, "
                "does not include 0z observation"
            ),
            axisbg="white",
        )
        if sector == "iowa" or len(sector) == 2:
            df2 = df[df["state"] == ("IA" if len(sector) > 2 else sector)]
            labels = df2.index.values
            mp.drawcounties()
            size = 14
        else:
            df2 = df
            labels = None
            size = 10
        mp.plot_values(
            df2["lon"].values,
            df2["lat"].values,
            df2["low"].values,
            fmt="%.0f",
            labels=labels,
            labelbuffer=1,
            textsize=size,
        )
        pqstr = (
            f"plot ac {now:%Y%m%d%H%M} "
            f"summary/{sector.lower()}_asos_12z_low.png "
            f"{sector.lower()}_asos_12z_low.png png"
        )
        LOG.info(pqstr)
        mp.postprocess(pqstr=pqstr)
        mp.close()


if __name__ == "__main__":
    main()
