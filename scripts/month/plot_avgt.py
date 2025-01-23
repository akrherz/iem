"""Plot the average temperature for the month"""

from datetime import date, datetime, timedelta

import numpy as np
from pyiem.database import get_dbconnc
from pyiem.plot import MapPlot


def main():
    """Go Main Go"""
    now = datetime.now()
    pgconn, icursor = get_dbconnc("iem")

    day1 = date.today().replace(day=1)
    day2 = (day1 + timedelta(days=35)).replace(day=1)

    lats = []
    lons = []
    vals = []
    valmask = []
    table = f"summary_{day1:%Y}"
    icursor.execute(
        f"""
        SELECT id, s.network, ST_x(s.geom) as lon, ST_y(s.geom) as lat,
        avg( (max_tmpf + min_tmpf)/2.0 ) as avgt , count(*) as cnt
        from {table} c JOIN stations s ON (s.iemid = c.iemid)
        WHERE s.network = 'IA_ASOS' and
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
        valmask.append(row["network"] == "IA_ASOS")
    pgconn.close()
    if len(vals) < 3:
        return

    mp = MapPlot(
        axisbg="white",
        title="Iowa %s Average Temperature" % (now.strftime("%Y %B"),),
        subtitle=("Average of the High + Low ending: %s")
        % (now.strftime("%d %B"),),
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
