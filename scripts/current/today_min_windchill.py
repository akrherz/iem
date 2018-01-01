"""
 Create a plot of minimum wind chill
"""
import datetime
import sys

import numpy as np
import pyiem.iemre as iemre
import netCDF4
import pytz
from pandas.io.sql import read_sql
from metpy.units import units
from metpy.calc import windchill
from pyiem.datatypes import distance
from pyiem.plot import MapPlot, nwsprecip
from pyiem.util import utc, get_dbconn
from pyiem.network import Table as NetworkTable


def doday(ts, realtime):
    """
    Create a plot of precipitation stage4 estimates for some day
    """
    nt = NetworkTable(['AWOS', 'IA_ASOS'])
    pgconn = get_dbconn('iem', user='nobody')
    df = read_sql("""
    SELECT id as station, tmpf, sknt from current_log c JOIN stations t
    on (c.iemid = t.iemid) WHERE t.network in ('IA_ASOS', 'AWOS')
    and valid >= %s and valid < %s + '24 hours'::interval
    and tmpf is not null and sknt > 0
    """, pgconn, params=(ts, ts), index_col=None)
    df['wcht'] = windchill(df['tmpf'].values * units.degF,
                           df['sknt'].values * units.knots
                           ).to(units.degF).magnitude
    gdf = df.groupby('station').min()
    routes = 'ac'
    if not realtime:
        routes = 'a'
    lons = []
    lats = []
    vals = []
    labels = []
    for station, row in gdf.iterrows():
        lons.append(nt.sts[station]['lon'])
        lats.append(nt.sts[station]['lat'])
        vals.append(row['wcht'])
        labels.append(station)

    pqstr = ("plot %s %s00 summary/iowa_min_windchill.png "
             "summary/iowa_min_windchill.png png"
             ) % (routes, ts.strftime("%Y%m%d%H"))
    mp = MapPlot(title=(r"%s Minimum Wind Chill Temperature $^\circ$F"
                        ) % (ts.strftime("%-d %b %Y"),),
                 subtitle="Calm conditions are excluded from analysis",
                 continentalcolor='white')

    mp.plot_values(lons, lats, vals, '%.1f', labels=labels, textsize=12,
                   labelbuffer=5, labeltextsize=10)
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr, view=False)
    mp.close()


def main():
    """Main Method"""
    if len(sys.argv) == 4:
        date = datetime.date(int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3]))
        realtime = False
    else:
        date = datetime.date.today()
        realtime = True
    doday(date, realtime)


if __name__ == "__main__":
    main()
