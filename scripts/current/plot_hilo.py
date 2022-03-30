""" Plot the High + Low Temperatures"""

import sys
import datetime
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go"""
    now = datetime.date.today()
    routes = "ac"
    if len(argv) == 4:
        routes = "a"
        now = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    # Compute normal from the climate database
    data = []
    icursor.execute(
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
    for row in icursor:
        data.append(
            dict(lat=row[4], lon=row[3], tmpf=row[1], dwpf=row[2], id=row[0])
        )

    mp = MapPlot(
        title="Iowa High & Low Air Temperature",
        axisbg="white",
        subtitle=now.strftime("%d %b %Y"),
    )
    mp.plot_station(data)
    mp.drawcounties()
    pqstr = "plot %s %s0000 bogus hilow.gif png" % (
        routes,
        now.strftime("%Y%m%d"),
    )
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main(sys.argv)
