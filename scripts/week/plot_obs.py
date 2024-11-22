"""Plot 7,31,91 Day Precipitation Totals.

Called from RUN_10_AFTER.sh
"""

from datetime import date, timedelta

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from sqlalchemy import text


def fmter(val):
    """Make pretty text"""
    if val is None:
        return 0
    if 0 < val < 0.009:
        return "T"
    return f"{val:.2f}"


def runner(days):
    """Go!"""
    today = date.today()
    routes = "ac"
    sixago = today - timedelta(days=days - 1)

    # Compute normal from the climate database
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text("""
            select s.id, ST_x(s.geom) as lon, ST_y(s.geom) as lat,
            sum(pday) as rainfall
            from summary c JOIN stations s on (c.iemid = s.iemid)
            WHERE day >= :sixago and day <= :today
            and s.network = 'IA_ASOS' and pday >= 0 and pday < 30
            GROUP by s.id, lon, lat
        """),
            conn,
            params={"sixago": sixago, "today": today},
            index_col="id",
        )
    df["label"] = df["rainfall"].apply(fmter)

    mp = MapPlot(
        title=f"Iowa {days} Day Precipitation Total [inch] (ASOS)",
        subtitle=f"{sixago:%d %b %Y} - {today:%d %b %Y} inclusive",
        continentalcolor="white",
    )
    mp.plot_values(
        df["lon"].values,
        df["lat"].values,
        df["label"].values,
        "%s",
        labels=df.index.values,
        labelbuffer=5,
    )
    mp.drawcounties()
    pqstr = (
        f"plot {routes} {today:%Y%m%d}0000 summary/{days}day/ia_precip.png "
        f"summary/{days}day/ia_precip.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


def main():
    """Go Main Go"""
    for days in [7, 31, 91]:
        runner(days)


if __name__ == "__main__":
    main()
