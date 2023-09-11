"""Plot the COOP Precipitation Reports, don't use lame-o x100"""

import datetime

from pyiem.plot import MapPlot
from pyiem.reference import TRACE_VALUE
from pyiem.util import get_dbconnc


def n(val):
    """pretty"""
    if val == TRACE_VALUE:
        return "T"
    if val == 0:
        return "0"
    return "%.2f" % (val,)


def main():
    """Go Main Go"""
    pgconn, icursor = get_dbconnc("iem")

    lats = []
    lons = []
    vals = []
    valmask = []
    labels = []
    icursor.execute(
        """
        select id, ST_x(s.geom) as lon, ST_y(s.geom) as lat, pday
        from summary c, stations s
        WHERE day = 'TODAY' and pday >= 0 and pday < 20
        and s.network = 'IA_COOP' and s.iemid = c.iemid
    """
    )
    for row in icursor:
        lats.append(row["lat"])
        lons.append(row["lon"])
        vals.append(n(row["pday"]))
        labels.append(row["id"])
        valmask.append(True)

    mp = MapPlot(
        title="Iowa COOP 24 Hour Precipitation",
        axisbg="white",
        subtitle="ending approximately %s 7 AM"
        % (datetime.datetime.now().strftime("%-d %b %Y"),),
    )
    mp.plot_values(lons, lats, vals)
    pqstr = "plot ac %s iowa_coop_precip.png iowa_coop_precip.png png" % (
        datetime.datetime.now().strftime("%Y%m%d%H%M"),
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
