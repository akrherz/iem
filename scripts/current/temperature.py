"""Generate current plot of Temperature"""
import datetime

from pandas.io.sql import read_sql
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def get_df():
    """Get my data"""
    pgconn = get_dbconn("iem", user="nobody")

    return read_sql(
        """
      SELECT s.id as station, s.network, tmpf, drct, sknt,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat
      FROM current c, stations s
      WHERE (s.network ~* 'ASOS' or s.network = 'AWOS')
      and s.country = 'US' and
      s.state not in ('HI', 'AK') and
      s.iemid = c.iemid and
      (valid + '30 minutes'::interval) > now() and
      tmpf >= -50 and tmpf < 140
    """,
        pgconn,
        index_col="station",
    )


def main():
    """GO!"""
    now = datetime.datetime.now()

    df = get_df()
    # df = pd.read_csv('example.csv')
    rng = range(-30, 120, 2)

    for sector in ["iowa", "midwest", "conus"]:
        mp = MapPlot(
            axisbg="white",
            sector=sector,
            title=("%s 2 meter Air Temperature") % (sector.capitalize(),),
            subtitle=now.strftime("%d %b %Y %-I:%M %p"),
        )
        mp.contourf(
            df["lon"].values,
            df["lat"].values,
            df["tmpf"].values,
            rng,
            clevstride=5,
            units="F",
        )
        mp.plot_values(
            df["lon"].values, df["lat"].values, df["tmpf"].values, fmt="%.0f"
        )
        if sector == "iowa":
            mp.drawcounties()
        pqstr = ("plot ac %s00 %s_tmpf.png %s_tmpf_%s.png png" "") % (
            datetime.datetime.utcnow().strftime("%Y%m%d%H"),
            sector,
            sector,
            datetime.datetime.utcnow().strftime("%H"),
        )
        mp.postprocess(view=False, pqstr=pqstr)
        mp.close()


if __name__ == "__main__":
    main()
