"""Output the 12z morning low temperature"""
import datetime

import matplotlib.cm as cm
import numpy as np
from pyiem.plot import MapPlot
from pyiem.tracker import loadqc
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    now = datetime.datetime.now()
    qdict = loadqc()
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor()

    sql = """
      select s.id,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat,
      max_tmpf as high, s.network
      from summary c, stations s
      WHERE c.iemid = s.iemid and day = 'TODAY' and max_tmpf > -40
      and s.network in ('IA_ASOS', 'AWOS', 'IL_ASOS','MO_ASOS','KS_ASOS',
      'NE_ASOS','SD_ASOS','MN_ASOS','WI_ASOS') ORDER by high ASC
    """

    lats = []
    lons = []
    vals = []
    valmask = []
    labels = []
    icursor.execute(sql)
    dsm = None
    for row in icursor:
        if row[0] == "DSM":
            dsm = row[3]
        if qdict.get(row[0], {}).get("tmpf") is not None:
            continue
        lats.append(row[2])
        lons.append(row[1])
        vals.append(row[3])
        labels.append(row[0])
        valmask.append(row[4] in ["AWOS", "IA_ASOS"])

    if len(lats) < 4:
        return

    mp = MapPlot(
        sector="iowa",
        title=("%s Iowa ASOS/AWOS High Temperature")
        % (now.strftime("%-d %b %Y"),),
        subtitle="map valid: %s" % (now.strftime("%d %b %Y %-I:%M %p"),),
    )
    # m.debug = True
    if dsm is None:
        dsm = vals[0]

    bottom = int(dsm) - 15
    top = int(dsm) + 15
    bins = np.linspace(bottom, top, 11)
    cmap = cm.get_cmap("jet")
    mp.contourf(lons, lats, vals, bins, units="F", cmap=cmap)
    mp.plot_values(
        lons,
        lats,
        vals,
        "%.0f",
        valmask=valmask,
        labels=labels,
        labelbuffer=10,
    )
    mp.drawcounties()

    pqstr = "plot ac %s summary/iowa_asos_high.png iowa_asos_high.png png" % (
        now.strftime("%Y%m%d%H%M"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
