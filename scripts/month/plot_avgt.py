""" Plot the average temperature for the month"""
import datetime

import numpy as np
import psycopg2.extras
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    now = datetime.datetime.now()
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    day1 = datetime.date.today().replace(day=1)
    day2 = (day1 + datetime.timedelta(days=35)).replace(day=1)

    lats = []
    lons = []
    vals = []
    valmask = []
    table = "summary_%s" % (day1.year,)
    icursor.execute(
        """
        SELECT id, s.network, ST_x(s.geom) as lon, ST_y(s.geom) as lat,
        avg( (max_tmpf + min_tmpf)/2.0 ) as avgt , count(*) as cnt
        from """
        + table
        + """ c JOIN stations s ON (s.iemid = c.iemid)
        WHERE s.network in ('IA_ASOS', 'AWOS') and
        day >= %s and day < %s
        and max_tmpf > -30 and min_tmpf < 90 GROUP by id, s.network, lon, lat
    """,
        (day1, day2),
    )
    for row in icursor:
        if row["cnt"] != now.day:
            continue
        lats.append(row["lat"])
        lons.append(row["lon"])
        vals.append(row["avgt"])
        valmask.append(row["network"] in ["AWOS", "IA_ASOS"])

    if len(vals) < 3:
        return

    mp = MapPlot(
        axisbg="white",
        title="Iowa %s Average Temperature" % (now.strftime("%Y %B"),),
        subtitle=("Average of the High + Low ending: %s" "") % (now.strftime("%d %B"),),
    )
    minval = int(min(vals))
    maxval = max([int(max(vals)) + 3, minval + 11])
    clevs = np.linspace(minval, maxval, 10, dtype="i")
    mp.contourf(lons, lats, vals, clevs)
    mp.drawcounties()
    mp.plot_values(lons, lats, vals, "%.1f")
    pqstr = "plot c 000000000000 summary/mon_mean_T.png bogus png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
