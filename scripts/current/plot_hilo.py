"""Plot the High + Low Temperatures.

Called from RUN_10_AFTER.sh and RUN_SUMMARY.sh
"""

from datetime import datetime

import click
import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from sqlalchemy import text


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Go Main Go"""
    now = dt.today()
    routes = "ac" if now == dt.today() else "a"

    # Compute normal from the climate database
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(
            text(f"""
    SELECT
      s.id, max_tmpf as tmpf, min_tmpf as dwpf,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat
    FROM
      summary_{now.year} c JOIN stations s on (c.iemid = s.iemid)
    WHERE
      s.network = 'IA_ASOS' and day = :dt
      and max_tmpf is not null and min_tmpf is not null
    """),
            conn,
            params={"dt": now},
        )

    mp = MapPlot(
        title="Iowa High & Low Air Temperature",
        axisbg="white",
        subtitle=now.strftime("%d %b %Y"),
    )
    mp.plot_station(obs.to_dict("records"))
    mp.drawcounties()
    pqstr = f"plot {routes} {now:%Y%m%d}0000 bogus hilow.gif png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
