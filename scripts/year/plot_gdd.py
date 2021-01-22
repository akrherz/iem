""" Generate a plot of GDD for the ASOS/AWOS network"""
import sys
import datetime

import numpy as np
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go"""
    st = NetworkTable("IACLIMATE")
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    pgconn = get_dbconn("coop", user="nobody")
    ccursor = pgconn.cursor()

    gfunc = "gdd50"
    gbase = 50
    if len(argv) == 2 and argv[1] == "gdd52":
        gfunc = "gdd52"
        gbase = 52
    if len(argv) == 2 and argv[1] == "gdd48":
        gfunc = "gdd48"
        gbase = 48

    # Compute normal from the climate database
    ccursor.execute(
        """
        SELECT station,
        sum(%s(high, low)) as gdd
        from alldata_ia WHERE station != 'IA0000'
        and substr(station, 3, 1) != 'C' and year = %s
        GROUP by station
    """
        % (gfunc, now.year)
    )

    lats = []
    lons = []
    gdd50 = []
    valmask = []

    for row in ccursor:
        station = row[0]
        if station not in st.sts:
            continue
        lats.append(st.sts[station]["lat"])
        lons.append(st.sts[station]["lon"])
        gdd50.append(float(row[1]))
        valmask.append(True)

    mp = MapPlot(
        axisbg="white",
        title=("Iowa %s GDD (base=%s) Accumulation")
        % (now.strftime("%Y"), gbase),
        subtitle="1 Jan - %s" % (now.strftime("%d %b %Y"),),
    )
    minval = min(gdd50)
    rng = max([int(max(gdd50) - minval), 10])
    ramp = np.linspace(minval, minval + rng, 10, dtype=np.int)
    if max(gdd50) > 0:
        mp.contourf(lons, lats, gdd50, ramp)
    pqstr = "plot c 000000000000 summary/gdd_jan1.png bogus png"
    if gbase == 52:
        pqstr = "plot c 000000000000 summary/gdd52_jan1.png bogus png"
    elif gbase == 48:
        pqstr = "plot c 000000000000 summary/gdd48_jan1.png bogus png"
    mp.drawcounties()
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main(sys.argv)
