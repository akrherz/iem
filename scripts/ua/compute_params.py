"""Compute sounding derived parameters."""
import sys

from pyiem.util import get_dbconn, utc, logger
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import pandas as pd
import numpy as np
from metpy.calc import (
    precipitable_water, surface_based_cape_cin, most_unstable_cape_cin,
    el, lfc, lcl
)
from metpy.units import units
LOG = logger()


def nonull(val):
    """Ensure we don't have NaN."""
    return val if not pd.isnull(val) else None


def log_interp(zz, xx, yy):
    """Log Interpolate."""
    # https://stackoverflow.com/questions/29346292
    logz = np.log10(zz)
    logx = np.log10(xx)
    logy = np.log10(yy)
    return np.power(10.0, np.interp(logz, logx, logy))


def get_station_elevation(df, nt):
    """See if we can determine the station elevation."""
    df2 = df[df['levelcode'] == 9]
    if not df2.empty:
        return df2.iloc[0]['height']
    res = nt.sts.get(df.iloc[0]['station'], {}).get('elevation')
    return 0 if res is None else res


def gt1(val):
    """Make sure our value is useful."""
    if val < 0.1:
        return None
    return val


def compute_total_totals(profile):
    """Total Totals."""
    # (T850 - T500) + (Td850 - T500)
    l850 = profile[profile['pressure'] == 850]
    l500 = profile[profile['pressure'] == 500]
    if l850.empty or l500.empty:
        return np.nan
    return (
        (l850.iloc[0]['tmpc'] - l500.iloc[0]['tmpc']) +
        (l850.iloc[0]['dwpc'] - l500.iloc[0]['tmpc'])
    )


def compute_sweat_index(profile, total_totals):
    """Compute the Sweat Index."""
    if pd.isnull(total_totals):
        return np.nan
    # 	SWET	= 12 * TD850 + 20 * TERM2 + 2 * SKT850 + SKT500 + SHEAR
    # TERM2	= MAX ( TOTL - 49, 0 )
    # TOTL	= Total totals index
    # SKT850	= 850 mb wind speed in knots
    # SKT500	= 500 mb wind speed in knots
    # SHEAR	= 125 * [ SIN ( DIR500 - DIR850 ) + .2 ]
    # DIR500	= 500 mb wind direction
    # DIR850	= 850 mb wind direction
    l850 = profile[profile['pressure'] == 850]
    l500 = profile[profile['pressure'] == 500]
    if l850.empty or l500.empty:
        return np.nan
    term2 = np.max([total_totals - 49., 0])
    skt850 = (
        l850.iloc[0]['smps'] * units("m/s")
    ).to(units.knots).m
    skt500 = (
        l500.iloc[0]['smps'] * units("m/s")
    ).to(units.knots).m
    dir500 = (l500.iloc[0]['drct'] * units("degrees_north")).to(units.radian).m
    dir850 = (l850.iloc[0]['drct'] * units("degrees_north")).to(units.radian).m
    shear = 125. * (np.sin(dir500 - dir850) + .2)
    return (
        12. * l850.iloc[0]['dwpc'] + 20. * term2 + 2 * skt850 + skt500 + shear
    )


def do_profile(cursor, fid, gdf, nt):
    """Process this profile."""
    profile = gdf[pd.notnull(gdf['tmpc']) & pd.notnull(gdf['dwpc'])]
    if profile.empty:
        LOG.info("profile %s is empty, skipping", fid)
        return
    if profile['pressure'].min() > 400:
        raise ValueError(
            "Profile only up to %s mb" % (profile['pressure'].min(), ))
    station_elevation_m = get_station_elevation(gdf, nt)
    total_totals = compute_total_totals(profile)
    sweat_index = compute_sweat_index(profile, total_totals)
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
    el_p, el_t = el(
        profile['pressure'].values * units.hPa,
        profile['tmpc'].values * units.degC,
        profile['dwpc'].values * units.degC,
    )
    lfc_p, lfc_t = lfc(
        profile['pressure'].values * units.hPa,
        profile['tmpc'].values * units.degC,
        profile['dwpc'].values * units.degC,
    )
    (lcl_p, lcl_t) = lcl(
        profile['pressure'].values[0] * units.hPa,
        profile['tmpc'].values[0] * units.degC,
        profile['dwpc'].values[0] * units.degC,
    )
    vals = [el_p.to(units('hPa')).m, lfc_p.to(units('hPa')).m,
            lcl_p.to(units('hPa')).m]
    [el_hght, lfc_hght, lcl_hght] = log_interp(
        np.array(vals, dtype='f'), profile['pressure'].values[::-1],
        profile['height'].values[::-1])
    el_agl = gt1(el_hght - station_elevation_m)
    lcl_agl = gt1(lcl_hght - station_elevation_m)
    lfc_agl = gt1(lfc_hght - station_elevation_m)
    args = (
        nonull(sbcape.to(units('joules / kilogram')).m),
        nonull(sbcin.to(units('joules / kilogram')).m),
        nonull(mucape.to(units('joules / kilogram')).m),
        nonull(mucin.to(units('joules / kilogram')).m),
        nonull(pwater.to(units('mm')).m),
        nonull(el_agl), nonull(el_p.to(units('hPa')).m),
        nonull(el_t.to(units.degC).m),
        nonull(lfc_agl), nonull(lfc_p.to(units('hPa')).m),
        nonull(lfc_t.to(units.degC).m),
        nonull(lcl_agl), nonull(lcl_p.to(units('hPa')).m),
        nonull(lcl_t.to(units.degC).m),
        nonull(total_totals), nonull(sweat_index),
        fid
    )
    print(args)
    cursor.execute("""
        UPDATE raob_flights SET sbcape_jkg = %s, sbcin_jkg = %s,
        mucape_jkg = %s, mucin_jkg = %s, pwater_mm = %s,
        el_agl_m = %s, el_pressure_hpa = %s, el_tmpc = %s,
        lfc_agl_m = %s, lfc_pressure_hpa = %s, lfc_tmpc = %s,
        lcl_agl_m = %s, lcl_pressure_hpa = %s, lcl_tmpc = %s,
        total_totals = %s, sweat_index = %s,
        computed = 't' WHERE fid = %s
    """, args)


def main(argv):
    """Go Main Go."""
    year = utc().year if len(argv) == 1 else int(argv[1])
    dbconn = get_dbconn('postgis')
    cursor = dbconn.cursor()
    nt = NetworkTable("RAOB")
    df = read_sql("""
        select f.fid, f.station, pressure, dwpc, tmpc, drct, smps, height,
        levelcode from
        raob_profile_""" + str(year) + """ p JOIN raob_flights f
        on (p.fid = f.fid) WHERE not computed
        ORDER by pressure DESC
    """, dbconn)
    count = 0
    for fid, gdf in df.groupby('fid'):
        try:
            do_profile(cursor, fid, gdf, nt)
        except (RuntimeError, ValueError, IndexError) as exp:
            LOG.info("Profile fid: %s failed calculation %s", fid, exp)
            cursor.execute("""
                UPDATE raob_flights SET computed = 't' WHERE fid = %s
            """, (fid, ))
        if count % 100 == 0:
            cursor.close()
            dbconn.commit()
            cursor = dbconn.cursor()
        count += 1
    cursor.close()
    dbconn.commit()


if __name__ == '__main__':
    main(sys.argv)
