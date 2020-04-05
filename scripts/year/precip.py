"""yearly precip"""
import datetime

import numpy as np
from pyiem.plot import MapPlot
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    st = NetworkTable("IACLIMATE")
    pgconn = get_dbconn("coop", user="nobody")
    ccursor = pgconn.cursor()

    ts = datetime.datetime.now() - datetime.timedelta(days=1)

    nrain = []
    lats = []
    lons = []

    # Get normals!
    ccursor.execute(
        """SELECT station, sum(precip) as acc from climate51
        WHERE valid <= '2000-%s' and station NOT IN ('IA7842','IA4381')
        and substr(station,0,3) = 'IA'
        GROUP by station ORDER by acc ASC"""
        % (ts.strftime("%m-%d"),)
    )
    for row in ccursor:
        station = row[0]
        if station not in st.sts:
            continue
        nrain.append(row[1])
        lats.append(st.sts[station]["lat"])
        lons.append(st.sts[station]["lon"])

    mp = MapPlot(
        axisbg="white",
        title=("Iowa %s Normal Precipitation Accumulation")
        % (ts.strftime("%Y"),),
        subtitle="1 Jan - %s" % (ts.strftime("%d %b %Y"),),
    )
    rng = np.arange(int(min(nrain)) - 1, int(max(nrain)) + 1)
    if max(nrain) < 10:
        rng = np.arange(0, 10)
    mp.contourf(lons, lats, nrain, rng, units="inch")
    pqstr = "plot c 000000000000 summary/year/normals.png bogus png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()

    # ----------------------------------
    # - Compute departures
    nrain = []
    lats = []
    lons = []
    ccursor.execute(
        """select climate.station, norm, obs from
        (select c.station, sum(c.precip) as norm from climate51 c
         where c.valid < '2000-%s' and substr(station,0,3) = 'IA'
         GROUP by c.station) as climate,
        (select a.station, sum(a.precip) as obs from alldata a
         WHERE a.year = %s and substr(a.station,0,3) = 'IA'
         GROUP by station) as obs
      WHERE obs.station = climate.station"""
        % (ts.strftime("%m-%d"), ts.year)
    )
    for row in ccursor:
        station = row[0]
        if station not in st.sts:
            continue
        nrain.append(row[2] - row[1])
        lats.append(st.sts[station]["lat"])
        lons.append(st.sts[station]["lon"])

    mp = MapPlot(
        axisbg="white",
        title=("Iowa %s Precipitation Depature") % (ts.strftime("%Y"),),
        subtitle="1 Jan - %s" % (ts.strftime("%d %b %Y"),),
    )
    rng = np.arange(int(min(nrain)) - 1, int(max(nrain)) + 1)
    if max(nrain) < 10:
        rng = np.arange(0, 10)
    mp.contourf(lons, lats, nrain, rng, units="inch")
    pqstr = "plot c 000000000000 summary/year/diff.png bogus png"
    mp.postprocess(view=False, pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
