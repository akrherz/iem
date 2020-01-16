"""Generate a map of the 12z UTC low temperature.

run from RUN_SUMMARY.sh
"""

from pyiem.plot import MapPlot
from pyiem.util import get_dbconn, utc, logger
from pandas.io.sql import read_sql

LOG = logger()


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem", user="nobody")
    now = utc().replace(hour=0, minute=0, second=0, microsecond=0)

    df = read_sql(
        """
    WITH lows as (
     SELECT c.iemid,
     min(tmpf) as calc_low,
     min(min_tmpf_6hr) as reported_low
     from current_log c JOIN stations s
     ON (s.iemid = c.iemid)
     WHERE valid > %s and valid < %s
     and (s.network ~* 'ASOS' or s.network = 'AWOS')
     and s.country = 'US' and s.state not in ('HI', 'AK') GROUP by c.iemid
    )

    select t.id, t.state, ST_x(t.geom) as lon, ST_y(t.geom) as lat,
    least(l.calc_low, l.reported_low) as low from
    lows l JOIN stations t on (t.iemid = l.iemid)
    """,
        pgconn,
        params=(now, now.replace(hour=12)),
        index_col="id",
    )
    df = df[df["low"].notnull()]
    LOG.debug("found %s observations for %s", len(df.index), now)

    for sector in ["iowa", "midwest", "conus"]:
        mp = MapPlot(
            sector=sector,
            title="%s ASOS/AWOS 01-12 UTC Low Temperature"
            % (now.strftime("%-d %b %Y"),),
            subtitle=(
                "includes available 6z and 12z 6-hr mins, "
                "does not include 0z observation"
            ),
            axisbg="white",
        )
        if sector == "iowa":
            df2 = df[df["state"] == "IA"]
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
            df2["low"],
            fmt="%.0f",
            labels=labels,
            labelbuffer=1,
            textsize=size,
        )
        pqstr = (
            "plot ac %s summary/%s_asos_12z_low.png " "%s_asos_12z_low.png png"
        ) % (now.strftime("%Y%m%d%H%M"), sector, sector)
        LOG.debug(pqstr)
        mp.postprocess(pqstr=pqstr)
        mp.close()


if __name__ == "__main__":
    main()
