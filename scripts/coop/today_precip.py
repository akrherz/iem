"""Plot the COOP Precipitation Reports, don't use lame-o x100

called from PREC.sh
"""

from datetime import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.plot import MapPlot
from pyiem.reference import TRACE_VALUE
from sqlalchemy import text


def n(val):
    """pretty"""
    if val == TRACE_VALUE:
        return "T"
    if val == 0:
        return "0"
    return f"{val:.2f}"


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(
            text("""
        select id, ST_x(s.geom) as lon, ST_y(s.geom) as lat, pday
        from summary c, stations s
        WHERE day = 'TODAY' and pday >= 0 and pday < 20
        and s.network = 'IA_COOP' and s.iemid = c.iemid
    """),
            conn,
            index_col=None,
        )

    mp = MapPlot(
        title="Iowa COOP 24 Hour Precipitation",
        axisbg="white",
        subtitle=f"ending approximately {datetime.now():%-d %b %Y} 7 AM",
    )
    mp.plot_values(obs["lon"], obs["lat"], obs["pday"].apply(n))
    pqstr = (
        f"plot ac {datetime.now():%Y%m%d%H%M} iowa_coop_precip.png "
        "iowa_coop_precip.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
