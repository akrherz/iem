"""Compute the Statewide and Climate District Averages!"""
from __future__ import print_function
import sys
import datetime

import netCDF4
import numpy as np
import geopandas as gpd
from pyiem import iemre
from pyiem.grid.zs import CachingZonalStats
from pyiem.datatypes import temperature, distance
from pyiem.util import get_dbconn

COOP = get_dbconn("coop")
ccursor = COOP.cursor()


def update_database(stid, valid, high, low, precip, snow, snowd):
    """Update the database with these newly computed values!"""
    table = "alldata_%s" % (stid[:2], )
    # See if we need to add an entry
    ccursor.execute("""SELECT day from """ + table + """ WHERE day = %s
    and station = %s""", (valid, stid))
    if ccursor.rowcount != 1:
        ccursor.execute("""INSERT into """ + table + """ (station, day,
        high, low, precip, snow, snowd, estimated, year, month, sday) VALUES
        (%s, %s, %s, %s, %s, %s, %s, 't', %s, %s, %s)
        """, (stid, valid, high, low, round(precip, 2),
              round(snow, 1), round(snowd, 1), valid.year,
              valid.month, valid.strftime("%m%d")))
    # Now we update
    ccursor.execute("""
        UPDATE """ + table + """
        SET high = %s, low = %s, precip = %s, snow = %s, snowd = %s
        WHERE station = %s and day = %s
    """, (high, low, round(precip, 2), round(snow, 1), round(snowd, 1),
          stid, valid))
    if ccursor.rowcount != 1:
        print('compute_0000:update_database updated %s row for %s %s' % (
            ccursor.rowcount, stid, valid))


def do_day(valid):
    """ Process a day please """
    idx = iemre.daily_offset(valid)
    nc = netCDF4.Dataset(iemre.get_daily_ncname(valid.year), 'r')
    high = temperature(nc.variables['high_tmpk_12z'][idx, :, :],
                       'K').value('F')
    low = temperature(nc.variables['low_tmpk_12z'][idx, :, :],
                      'K').value('F')
    precip = distance(nc.variables['p01d_12z'][idx, :, :], 'MM').value("IN")
    snow = distance(nc.variables['snow_12z'][idx, :, :], 'MM').value("IN")
    snowd = distance(nc.variables['snowd_12z'][idx, :, :], 'MM').value("IN")
    nc.close()

    # build out the state mappers
    pgconn = get_dbconn('postgis')
    states = gpd.GeoDataFrame.from_postgis("""
    SELECT the_geom, state_abbr from states
    where state_abbr not in ('AK', 'HI')
    """, pgconn, index_col='state_abbr', geom_col='the_geom')
    czs = CachingZonalStats(iemre.AFFINE)
    sthigh = czs.gen_stats(np.flipud(high), states['the_geom'])
    stlow = czs.gen_stats(np.flipud(low), states['the_geom'])
    stprecip = czs.gen_stats(np.flipud(precip), states['the_geom'])
    stsnow = czs.gen_stats(np.flipud(snow), states['the_geom'])
    stsnowd = czs.gen_stats(np.flipud(snowd), states['the_geom'])

    for i, state in enumerate(states.index.values):
        update_database(state+"0000", valid, sthigh[i], stlow[i],
                        stprecip[i], stsnow[i], stsnowd[i])

    # build out climate division mappers
    climdiv = gpd.GeoDataFrame.from_postgis("""
    SELECT geom, iemid from climdiv
    where st_abbrv not in ('AK', 'HI')
    """, pgconn, index_col='iemid', geom_col='geom')
    czs = CachingZonalStats(iemre.AFFINE)
    sthigh = czs.gen_stats(np.flipud(high), climdiv['geom'])
    stlow = czs.gen_stats(np.flipud(low), climdiv['geom'])
    stprecip = czs.gen_stats(np.flipud(precip), climdiv['geom'])
    stsnow = czs.gen_stats(np.flipud(snow), climdiv['geom'])
    stsnowd = czs.gen_stats(np.flipud(snowd), climdiv['geom'])

    for i, iemid in enumerate(climdiv.index.values):
        update_database(iemid, valid, sthigh[i], stlow[i],
                        stprecip[i], stsnow[i], stsnowd[i])


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        do_day(datetime.date(int(argv[1]), int(argv[2]),
                             int(argv[3])))
    elif len(argv) == 3:
        sts = datetime.date(int(argv[1]), int(argv[2]), 1)
        ets = sts + datetime.timedelta(days=35)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do_day(now)
            now += datetime.timedelta(days=1)
    else:
        do_day(datetime.date.today())


if __name__ == '__main__':
    main(sys.argv)
    ccursor.close()
    COOP.commit()
