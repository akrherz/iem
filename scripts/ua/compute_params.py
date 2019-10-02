"""Compute sounding derived parameters."""
import sys

from pyiem.util import get_dbconn, utc, logger
from pandas.io.sql import read_sql
import pandas as pd
from metpy.calc import (
    precipitable_water, surface_based_cape_cin, most_unstable_cape_cin
)
from metpy.units import units
LOG = logger()


def nonull(val):
    """Ensure we don't have NaN."""
    return val if not pd.isnull(val) else None


def do_profile(cursor, fid, gdf):
    """Process this profile."""
    profile = gdf[pd.notnull(gdf['tmpc']) & pd.notnull(gdf['dwpc'])]
    if profile.empty:
        LOG.info("profile %s is empty, skipping", fid)
        return
    if profile['pressure'].min() > 400:
        raise ValueError(
            "Profile only up to %s mb" % (profile['pressure'].min(), ))
    pwater = precipitable_water(
        profile['dwpc'].values * units.degC,
        profile['pressure'].values * units.hPa)
    (sbcape, sbcin) = surface_based_cape_cin(
        profile['pressure'].values * units.hPa,
        profile['tmpc'].values * units.degC,
        profile['dwpc'].values * units.degC, )
    (mucape, mucin) = most_unstable_cape_cin(
        profile['pressure'].values * units.hPa,
        profile['tmpc'].values * units.degC,
        profile['dwpc'].values * units.degC, )
    cursor.execute("""
        UPDATE raob_flights SET sbcape_jkg = %s, sbcin_jkg = %s,
        mucape_jkg = %s, mucin_jkg = %s, pwater_mm = %s,
        computed = 't' WHERE fid = %s
    """, (
        nonull(sbcape.to(units('joules / kilogram')).m),
        nonull(sbcin.to(units('joules / kilogram')).m),
        nonull(mucape.to(units('joules / kilogram')).m),
        nonull(mucin.to(units('joules / kilogram')).m),
        nonull(pwater.to(units('mm')).m), fid
    ))


def main(argv):
    """Go Main Go."""
    year = utc().year if len(argv) == 1 else int(argv[1])
    dbconn = get_dbconn('postgis')
    cursor = dbconn.cursor()
    df = read_sql("""
        select f.fid, pressure, dwpc, tmpc, drct, smps, height from
        raob_profile_""" + str(year) + """ p JOIN raob_flights f
        on (p.fid = f.fid) WHERE not computed
        ORDER by pressure DESC
    """, dbconn)
    for fid, gdf in df.groupby('fid'):
        try:
            do_profile(cursor, fid, gdf)
        except (RuntimeError, ValueError) as exp:
            LOG.info("Profile fid: %s failed calculation %s", fid, exp)
            cursor.execute("""
                UPDATE raob_flights SET computed = 't' WHERE fid = %s
            """, (fid, ))
    cursor.close()
    dbconn.commit()


if __name__ == '__main__':
    main(sys.argv)
