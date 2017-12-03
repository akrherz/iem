"""
 Generate analysis of Peak Wind Gust
"""
from __future__ import print_function
import datetime

import numpy as np
from pyiem.plot import MapPlot
from pyiem.datatypes import speed
from pyiem.util import get_dbconn
# contour.py:370: RuntimeWarning: invalid value encountered in true_divide
np.seterr(divide='ignore', invalid='ignore')


def main():
    """Go Main Go"""

    now = datetime.datetime.now()
    pgconn = get_dbconn('iem', user='nobody')
    icursor = pgconn.cursor()

    # Compute normal from the climate database
    sql = """
      select s.id, s.network,
      ST_x(s.geom) as lon, ST_y(s.geom) as lat,
      greatest(c.max_sknt, c.max_gust) as wind
      from summary_%s c, current c2, stations s
      WHERE s.iemid = c.iemid and c2.valid > 'TODAY' and c.day = 'TODAY'
      and c2.iemid = s.iemid
      and (s.network ~* 'ASOS' or s.network = 'AWOS') and s.country = 'US'
      ORDER by lon, lat
    """ % (now.year,)

    lats = []
    lons = []
    vals = []
    valmask = []
    icursor.execute(sql)
    for row in icursor:
        if row[4] == 0 or row[4] is None:
            continue
        lats.append(row[3])
        lons.append(row[2])
        vals.append(speed(row[4], 'KT').value('MPH'))
        valmask.append((row[1] in ['AWOS', 'IA_ASOS']))

    if len(vals) < 5 or True not in valmask:
        return

    clevs = np.arange(0, 40, 2)
    clevs = np.append(clevs, np.arange(40, 80, 5))
    clevs = np.append(clevs, np.arange(80, 120, 10))

    # Iowa
    pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
            now.strftime("%Y%m%d%H%M"), )
    mp = MapPlot(title="Iowa ASOS/AWOS Peak Wind Speed Reports",
                 subtitle="%s" % (now.strftime("%d %b %Y"), ),
                 sector='iowa')
    mp.contourf(lons, lats, vals, clevs, units='MPH')
    mp.plot_values(lons, lats, vals, '%.0f', valmask=valmask,
                   labelbuffer=10)
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr, view=False)
    mp.close()


if __name__ == '__main__':
    main()
