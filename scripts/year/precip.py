"""yearly precip"""

import datetime
import os
import subprocess
import tempfile

import numpy as np
import requests
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    st = NetworkTable("IACLIMATE")
    pgconn = get_dbconn("coop")
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
    # - Departures
    service = (
        "http://iem.local/plotting/auto/plot/97/d:sector::sector:IA::"
        f"var:precip_departdate1:{ts.year}-01-01::usdm:no::"
        f"date2:{ts:%Y-%m-%d}::p:contour::cmap:RdYlBu::c:yes::"
        "ct:ncei_climate91::_r:43::_cb:1.png"
    )

    req = requests.get(service, timeout=120)
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(req.content)
    tmpfd.close()

    pqstr = f"plot c {ts:%Y%m%d%H%M} summary/year/diff.png bogus png"
    subprocess.call(f"pqinsert -i -p '{pqstr}' {tmpfd.name}", shell=True)
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
