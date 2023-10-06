""" Plot the High + Low Temperatures"""

import datetime
import sys

from pyiem.plot import MapPlot
from pyiem.util import get_dbconnc


def main(argv):
    """Go Main Go"""
    now = datetime.date.today()
    routes = "ac"
    if len(argv) == 4:
        routes = "a"
        now = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    pgconn, cursor = get_dbconnc("iem")

    # Compute normal from the climate database
    data = []
    cursor.execute(
        f"""
    SELECT
      s.id as station, max_tmpf, min_tmpf,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat
    FROM
      summary_{now.year} c JOIN stations s on (c.iemid = s.iemid)
    WHERE
      s.network = 'IA_ASOS' and day = %s
      and max_tmpf is not null and min_tmpf is not null
    """,
        (now,),
    )
    for row in cursor:
        data.append(
            {
                "lat": row["lat"],
                "lon": row["lon"],
                "tmpf": row["max_tmpf"],
                "dwpf": row["min_tmpf"],
                "id": row["station"],
            }
        )
    pgconn.close()

    mp = MapPlot(
        title="Iowa High & Low Air Temperature",
        axisbg="white",
        subtitle=now.strftime("%d %b %Y"),
    )
    mp.plot_station(data)
    mp.drawcounties()
    pqstr = f"plot {routes} {now:%Y%m%d}0000 bogus hilow.gif png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main(sys.argv)
