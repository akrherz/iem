"""Generate a map of the 00z high temperature.

run from RUN_0Z.sh
"""
import datetime

from pyiem.plot import MapPlot
from pyiem.util import get_sqlalchemy_conn, utc, logger
import pandas as pd
from sqlalchemy import text

LOG = logger()


def main():
    """Go Main Go"""
    now = utc().replace(hour=0, minute=0, second=0, microsecond=0)
    sts = now - datetime.timedelta(hours=12)
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
                """
        WITH highs as (
        SELECT c.iemid,
        max(tmpf) as calc_high,
        max(max_tmpf_6hr) as reported_high
        from current_log c JOIN stations s
        ON (s.iemid = c.iemid)
        WHERE valid >= :sts and valid < :ets
        and s.network ~* 'ASOS'
        and s.country = 'US' and s.state not in ('HI', 'AK') GROUP by c.iemid
        )

        select t.id, t.state, ST_x(t.geom) as lon, ST_y(t.geom) as lat,
        greatest(l.calc_high, l.reported_high) as high from
        highs l JOIN stations t on (t.iemid = l.iemid)
        """
            ),
            conn,
            params={"sts": sts, "ets": now},
            index_col="id",
        )
    df = df[df["high"].notnull()]
    LOG.info("found %s observations for %s", len(df.index), now)

    for sector in ["iowa", "midwest"]:
        mp = MapPlot(
            sector=sector if len(sector) > 2 else "state",
            state=sector if len(sector) == 2 else "IA",
            title=f"{sts:%-d %b %Y} ASOS 12-00 UTC High Temperature",
            subtitle=("includes available 18z and 0z 6-hr maxes"),
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
            df2["high"].values,
            fmt="%.0f",
            labels=labels,
            labelbuffer=1,
            textsize=size,
        )
        pqstr = (
            f"plot ac {sts:%Y%m%d%H%M} "
            f"summary/{sector.lower()}_asos_0z_high.png "
            f"{sector.lower()}_asos_0z_high.png png"
        )
        LOG.info(pqstr)
        mp.postprocess(pqstr=pqstr)
        mp.close()


if __name__ == "__main__":
    main()
