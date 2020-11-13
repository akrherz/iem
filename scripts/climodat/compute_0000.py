"""Compute the Statewide and Climate District Averages!"""
import sys
import datetime
import warnings

import numpy as np
import geopandas as gpd
from pyiem import iemre
from pyiem.grid.zs import CachingZonalStats
from pyiem.datatypes import temperature, distance
from pyiem.util import get_dbconn, ncopen, logger

LOG = logger()
warnings.filterwarnings("ignore", category=FutureWarning)
COOP = get_dbconn("coop")
ccursor = COOP.cursor()


def zero(val):
    """Make masked values a zero"""
    if val is np.ma.masked:
        return 0
    return val


def update_database(stid, valid, row):
    """Update the database with these newly computed values!"""
    table = "alldata_%s" % (stid[:2],)

    def do_update(_row):
        """Do the database work, please."""
        ccursor.execute(
            """
            UPDATE """
            + table
            + """
            SET high = %s, low = %s, precip = %s, snow = %s, snowd = %s
            WHERE station = %s and day = %s
        """,
            (
                _row["high"],
                _row["low"],
                round(zero(_row["precip"]), 2),
                round(zero(_row["snow"]), 1),
                round(zero(_row["snowd"]), 1),
                stid,
                valid,
            ),
        )
        return ccursor.rowcount == 1

    if not do_update(row):
        ccursor.execute(
            f"INSERT into {table} (station, day, temp_estimated, "
            "precip_estimated, year, month, sday) VALUES "
            "(%s, %s, 't', 't', %s, %s, %s)",
            (stid, valid, valid.year, valid.month, valid.strftime("%m%d")),
        )
        do_update(row)


def do_day(valid):
    """ Process a day please """
    idx = iemre.daily_offset(valid)
    with ncopen(iemre.get_daily_ncname(valid.year), "r", timeout=300) as nc:
        high = temperature(
            nc.variables["high_tmpk_12z"][idx, :, :], "K"
        ).value("F")
        low = temperature(nc.variables["low_tmpk_12z"][idx, :, :], "K").value(
            "F"
        )
        precip = distance(nc.variables["p01d_12z"][idx, :, :], "MM").value(
            "IN"
        )
        snow = distance(nc.variables["snow_12z"][idx, :, :], "MM").value("IN")
        snowd = distance(nc.variables["snowd_12z"][idx, :, :], "MM").value(
            "IN"
        )

    # build out the state mappers
    pgconn = get_dbconn("postgis")
    states = gpd.GeoDataFrame.from_postgis(
        "SELECT the_geom, state_abbr from states "
        "where state_abbr not in ('AK', 'HI', 'DC')",
        pgconn,
        index_col="state_abbr",
        geom_col="the_geom",
    )
    czs = CachingZonalStats(iemre.AFFINE)
    sthigh = czs.gen_stats(np.flipud(high), states["the_geom"])
    stlow = czs.gen_stats(np.flipud(low), states["the_geom"])
    stprecip = czs.gen_stats(np.flipud(precip), states["the_geom"])
    stsnow = czs.gen_stats(np.flipud(snow), states["the_geom"])
    stsnowd = czs.gen_stats(np.flipud(snowd), states["the_geom"])

    statedata = {}
    for i, state in enumerate(states.index.values):
        statedata[state] = dict(
            high=sthigh[i],
            low=stlow[i],
            precip=stprecip[i],
            snow=stsnow[i],
            snowd=stsnowd[i],
        )
        update_database(state + "0000", valid, statedata[state])

    # build out climate division mappers
    climdiv = gpd.GeoDataFrame.from_postgis(
        "SELECT geom, iemid from climdiv "
        "where st_abbrv not in ('AK', 'HI', 'DC')",
        pgconn,
        index_col="iemid",
        geom_col="geom",
    )
    czs = CachingZonalStats(iemre.AFFINE)
    sthigh = czs.gen_stats(np.flipud(high), climdiv["geom"])
    stlow = czs.gen_stats(np.flipud(low), climdiv["geom"])
    stprecip = czs.gen_stats(np.flipud(precip), climdiv["geom"])
    stsnow = czs.gen_stats(np.flipud(snow), climdiv["geom"])
    stsnowd = czs.gen_stats(np.flipud(snowd), climdiv["geom"])

    for i, iemid in enumerate(climdiv.index.values):
        row = dict(
            high=sthigh[i],
            low=stlow[i],
            precip=stprecip[i],
            snow=stsnow[i],
            snowd=stsnowd[i],
        )
        # we must have temperature data
        if row["high"] is np.ma.masked or row["low"] is np.ma.masked:
            LOG.info("%s has missing temperature data, using state", iemid)
            row = statedata[iemid[:2]]
        update_database(iemid, valid, row)


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        do_day(datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))
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


if __name__ == "__main__":
    main(sys.argv)
    ccursor.close()
    COOP.commit()
