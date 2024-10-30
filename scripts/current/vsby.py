"""Generate current plot of visibility"""

import warnings
from datetime import datetime

import numpy as np
from pyiem.database import get_dbconn
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import utc

# Stop whining about missing data for contourf
warnings.filterwarnings("ignore")


def main():
    """GO"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    # Compute normal from the climate database
    sql = """
    SELECT
      id, network, vsby, ST_x(geom) as lon, ST_y(geom) as lat
    FROM
      current c JOIN stations s ON (s.iemid = c.iemid)
    WHERE
      s.network IN ('IA_ASOS','IL_ASOS','MN_ASOS','WI_ASOS','SD_ASOS',
                  'NE_ASOS','MO_ASOS') and
      valid + '60 minutes'::interval > now() and
      vsby >= 0 and vsby <= 10
    """

    lats = []
    lons = []
    vals = []
    valmask = []
    cursor.execute(sql)
    for row in cursor:
        lats.append(row[4])
        lons.append(row[3])
        vals.append(row[2])
        valmask.append(row[1] == "IA_ASOS")

    if len(lats) < 5:
        return

    now = datetime.now()

    mp = MapPlot(
        sector="iowa",
        title="Iowa Visibility",
        subtitle=f"Valid: {now:%d %b %Y %-I:%M %p}",
    )

    mp.contourf(
        lons,
        lats,
        vals,
        np.array([0.01, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 9.9]),
        units="miles",
        cmap=get_cmap("gray"),
    )

    mp.plot_values(lons, lats, vals, "%.1f", valmask)
    mp.drawcounties()

    pqstr = (
        f"plot ac {utc():%Y%m%d%H}00 iowa_vsby.png "
        f"vsby_contour_{utc():%H}00.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
