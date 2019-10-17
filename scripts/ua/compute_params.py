"""Compute sounding derived parameters."""
import sys

from pyiem.util import get_dbconn, utc, logger
from pyiem.network import Table as NetworkTable
from pandas.io.sql import read_sql
import pandas as pd
import numpy as np
from metpy.calc import (
    precipitable_water, surface_based_cape_cin, most_unstable_cape_cin,
    el, lfc, lcl, bunkers_storm_motion, wind_components, wind_direction,
    wind_speed, storm_relative_helicity
)
from metpy.units import units
LOG = logger()


def nonull(val):
    """Ensure we don't have NaN."""
    return np.array(val).item() if not pd.isnull(val) else None


def log_interp(zz, xx, yy):
    """Log Interpolate."""
    # https://stackoverflow.com/questions/29346292
    logz = np.log10(zz)
    logx = np.log10(xx)
    logy = np.log10(yy)
    return np.power(10.0, np.interp(logz, logx, logy))


def get_station_elevation(df, nt):
    """See if we can determine the station elevation."""
    metadata_says = nt.sts.get(df.iloc[0]['station'], {}).get('elevation')
    df2 = df[df['levelcode'] == 9]
    data_says = df.iloc[0]['height'] if df2.empty else df2.iloc[0]['height']
    if metadata_says is None:
        return data_says
    if np.abs(data_says - metadata_says) > 49:
        raise RuntimeError((
            "lowest level %.1f too far from station: %.1f"
            ) % (data_says, metadata_says))
    return data_says


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
    # The inbound profile may contain mandatory level data that is below
    # the surface.  It seems the best we can do here is to ensure both
    # temperature and dewpoint are valid and call that the bottom.
    td_profile = gdf[pd.notnull(gdf['tmpc']) & pd.notnull(gdf['dwpc'])]
    wind_profile = gdf[pd.notnull(gdf['u'])]
    if td_profile.empty or wind_profile.empty:
        LOG.info("profile %s is empty, skipping", fid)
        return
    if gdf['pressure'].min() > 500:
        raise ValueError(
            "Profile only up to %s mb" % (gdf['pressure'].min(), ))
    # Does a crude check that our metadata station elevation is within 50m
    # of the profile bottom, otherwise we ABORT
    station_elevation_m = get_station_elevation(td_profile, nt)
    total_totals = compute_total_totals(td_profile)
    sweat_index = compute_sweat_index(td_profile, total_totals)
    try:
        bunkers_rm, bunkers_lm, mean0_6_wind = bunkers_storm_motion(
            wind_profile['pressure'].values * units.hPa,
            wind_profile['u'].values * units("m/s"),
            wind_profile['v'].values * units("m/s"),
            wind_profile['height'].values * units("m")
        )
    except ValueError:
        # Profile may not go up high enough
        bunkers_rm = [np.nan * units('m/s'), np.nan * units('m/s')]
        bunkers_lm = [np.nan * units('m/s'), np.nan * units('m/s')]
        mean0_6_wind = [np.nan * units('m/s'), np.nan * units('m/s')]
    bunkers_rm_smps = wind_speed(bunkers_rm[0], bunkers_rm[1])
    bunkers_rm_drct = wind_direction(bunkers_rm[0], bunkers_rm[1])
    bunkers_lm_smps = wind_speed(bunkers_lm[0], bunkers_lm[1])
    bunkers_lm_drct = wind_direction(bunkers_lm[0], bunkers_lm[1])
    mean0_6_wind_smps = wind_speed(mean0_6_wind[0], mean0_6_wind[1])
    mean0_6_wind_drct = wind_direction(mean0_6_wind[0], mean0_6_wind[1])
    try:
        (srh_sfc_1km_pos, srh_sfc_1km_neg,
         srh_sfc_1km_total) = storm_relative_helicity(
             wind_profile['u'].values * units('m/s'),
             wind_profile['v'].values * units('m/s'),
             wind_profile['height'].values * units('m'),
             1000. * units('m')
         )
    except ValueError:
        srh_sfc_1km_pos = np.nan * units('m')  # blah
        srh_sfc_1km_neg = np.nan * units('m')  # blah
        srh_sfc_1km_total = np.nan * units('m')  # blah
    try:
        (srh_sfc_3km_pos, srh_sfc_3km_neg,
         srh_sfc_3km_total) = storm_relative_helicity(
             wind_profile['u'].values * units('m/s'),
             wind_profile['v'].values * units('m/s'),
             wind_profile['height'].values * units('m'),
             3000. * units('m')
         )
    except ValueError:
        srh_sfc_3km_pos = np.nan * units('m')  # blah
        srh_sfc_3km_neg = np.nan * units('m')  # blah
        srh_sfc_3km_total = np.nan * units('m')  # blah
    pwater = precipitable_water(
        td_profile['dwpc'].values * units.degC,
        td_profile['pressure'].values * units.hPa)
    (sbcape, sbcin) = surface_based_cape_cin(
        td_profile['pressure'].values * units.hPa,
        td_profile['tmpc'].values * units.degC,
        td_profile['dwpc'].values * units.degC, )
    (mucape, mucin) = most_unstable_cape_cin(
        td_profile['pressure'].values * units.hPa,
        td_profile['tmpc'].values * units.degC,
        td_profile['dwpc'].values * units.degC, )
    el_p, el_t = el(
        td_profile['pressure'].values * units.hPa,
        td_profile['tmpc'].values * units.degC,
        td_profile['dwpc'].values * units.degC,
    )
    lfc_p, lfc_t = lfc(
        td_profile['pressure'].values * units.hPa,
        td_profile['tmpc'].values * units.degC,
        td_profile['dwpc'].values * units.degC,
    )
    (lcl_p, lcl_t) = lcl(
        td_profile['pressure'].values[0] * units.hPa,
        td_profile['tmpc'].values[0] * units.degC,
        td_profile['dwpc'].values[0] * units.degC,
    )
    vals = [el_p.to(units('hPa')).m, lfc_p.to(units('hPa')).m,
            lcl_p.to(units('hPa')).m]
    [el_hght, lfc_hght, lcl_hght] = log_interp(
        np.array(vals, dtype='f'), td_profile['pressure'].values[::-1],
        td_profile['height'].values[::-1])
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
        nonull(bunkers_rm_smps.m), nonull(bunkers_rm_drct.m),
        nonull(bunkers_lm_smps.m), nonull(bunkers_lm_drct.m),
        nonull(mean0_6_wind_smps.m), nonull(mean0_6_wind_drct.m),
        nonull(srh_sfc_1km_pos.m), nonull(srh_sfc_1km_neg.m),
        nonull(srh_sfc_1km_total.m),
        nonull(srh_sfc_3km_pos.m), nonull(srh_sfc_3km_neg.m),
        nonull(srh_sfc_3km_total.m),
        fid
    )
    cursor.execute("""
        UPDATE raob_flights SET sbcape_jkg = %s, sbcin_jkg = %s,
        mucape_jkg = %s, mucin_jkg = %s, pwater_mm = %s,
        el_agl_m = %s, el_pressure_hpa = %s, el_tmpc = %s,
        lfc_agl_m = %s, lfc_pressure_hpa = %s, lfc_tmpc = %s,
        lcl_agl_m = %s, lcl_pressure_hpa = %s, lcl_tmpc = %s,
        total_totals = %s, sweat_index = %s,
        bunkers_rm_smps = %s, bunkers_rm_drct = %s,
        bunkers_lm_smps = %s, bunkers_lm_drct = %s,
        mean_sfc_6km_smps = %s, mean_sfc_6km_drct = %s,
        srh_sfc_1km_pos = %s, srh_sfc_1km_neg = %s, srh_sfc_1km_total = %s,
        srh_sfc_3km_pos = %s, srh_sfc_3km_neg = %s, srh_sfc_3km_total = %s,
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
    if df.empty:
        return
    df['u'], df['v'] = wind_components(
        df['smps'].values * units('m/s'),
        df['drct'].values * units("degrees_north")
    )
    count = 0
    for fid, gdf in df.groupby('fid'):
        try:
            do_profile(cursor, fid, gdf, nt)
        except (RuntimeError, ValueError, IndexError) as exp:
            LOG.info(
                "Profile %s fid: %s failed calculation %s",
                gdf.iloc[0]['station'], fid, exp)
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
