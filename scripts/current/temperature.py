"""Generate current plot of Temperature"""
import datetime

import pandas as pd
from pyiem.plot import MapPlot
from pyiem.util import get_sqlalchemy_conn, utc


def get_df():
    """Get my data"""
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            """
        SELECT s.id as station, s.network, tmpf, drct, sknt,
        ST_x(s.geom) as lon, ST_y(s.geom) as lat
        FROM current c, stations s
        WHERE s.network ~* 'ASOS' and s.country = 'US' and
        s.state not in ('HI', 'AK') and
        s.iemid = c.iemid and
        (valid + '30 minutes'::interval) > now() and
        tmpf >= -50 and tmpf < 140
        """,
            conn,
            index_col="station",
        )
    return df


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
            title=f"{sector.capitalize()} 2 meter Air Temperature",
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
        pqstr = (
            f"plot ac {utc():%Y%m%d%H}00 {sector}_tmpf.png "
            f"{sector}_tmpf_{utc():%H}.png png"
        )
        mp.postprocess(view=False, pqstr=pqstr)
        mp.close()


if __name__ == "__main__":
    main()
