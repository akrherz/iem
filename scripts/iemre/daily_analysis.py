"""Grid the daily data onto a grid for IEMRE

This is tricky as some variables we can compute sooner than others.  We run
this script twice per day:

    RUN_MIDNIGHT.sh for just the 'calendar day' variables yesterday
    RUN_NOON.sh for the 12z today vals and calendar day yesterday
"""
import datetime
import os
import subprocess
import sys

import numpy as np
from metpy.interpolate import inverse_distance_to_grid
from pandas.io.sql import read_sql
from pyiem import iemre
from pyiem.util import convert_value, get_dbconnstr, logger, ncopen, utc
from scipy.stats import zscore

PGCONN = get_dbconnstr("iem")
COOP_PGCONN = get_dbconnstr("coop")
LOG = logger()


def generic_gridder(df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    if df[idx].max() == 0 and df[idx].max() == 0:
        return np.zeros((iemre.NY, iemre.NX))
    window = 2.0
    f1 = df[df[idx].notnull()]
    for lat in np.arange(iemre.SOUTH, iemre.NORTH, window):
        for lon in np.arange(iemre.WEST, iemre.EAST, window):
            (west, east, south, north) = (lon, lon + window, lat, lat + window)
            box = f1[
                (f1["lat"] >= south)
                & (f1["lat"] < north)
                & (f1["lon"] >= west)
                & (f1["lon"] < east)
            ]
            # can't QC data that is all equal
            if len(box.index) < 4 or box[idx].min() == box[idx].max():
                continue
            z = np.abs(zscore(box[idx]))
            # Compute where the standard dev is +/- 2std
            bad = box[z > 1.5]
            df.loc[bad.index, idx] = np.nan

    df2 = df[df[idx].notnull()]
    if len(df2.index) < 4:
        LOG.warning("Not enough data %s", idx)
        return None
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    res = np.ones(xi.shape) * np.nan
    # do our gridding
    grid = inverse_distance_to_grid(
        df2["lon"].values, df2["lat"].values, df2[idx].values, xi, yi, 1.5
    )
    # replace nan values in res with whatever now is in grid
    res = np.where(np.isnan(res), grid, res)
    # Do we still have missing values?
    if np.isnan(res).any():
        # very aggressive with search radius
        grid = inverse_distance_to_grid(
            df2["lon"].values, df2["lat"].values, df2[idx].values, xi, yi, 5.5
        )
        # replace nan values in res with whatever now is in grid
        res = np.where(np.isnan(res), grid, res)
    # replace sentinel back to np.nan
    res = np.where(res == -9999, np.nan, res)
    return np.ma.array(res, mask=np.isnan(res))


def copy_iemre(ts, ds):
    """Compute the 6 UTC to 6 UTC totals via IEMRE hourly values."""
    sts = utc(ts.year, ts.month, ts.day, 6)
    ets = sts + datetime.timedelta(hours=24)
    offset = iemre.daily_offset(ts)
    offset1 = iemre.hourly_offset(sts)
    offset2 = iemre.hourly_offset(ets)
    windhours = 0
    if ts.month == 12 and ts.day == 31:
        LOG.warning(
            "p01d      for %s [idx:%s] %s(%s)->%s(%s) SPECIAL",
            ts,
            offset,
            sts.strftime("%Y%m%d%H"),
            offset1,
            ets.strftime("%Y%m%d%H"),
            offset2,
        )
        ncfn = iemre.get_hourly_ncname(ets.year)
        if not os.path.isfile(ncfn):
            LOG.warning("Missing %s", ncfn)
            return
        with ncopen(ncfn, timeout=600) as hnc:
            phour = np.sum(hnc.variables["p01m"][:offset2, :, :], 0)
            sped = None
            for offset in range(offset2):
                uwnd = hnc.variables["uwnd"][offset, :, :]
                vwnd = hnc.variables["vwnd"][offset, :, :]
                if uwnd.mask.all():
                    LOG.warning("No wind for offset: %s", offset)
                    continue
                mag = (uwnd**2 + vwnd**2) ** 0.5
                windhours += 1
                if sped is None:
                    sped = mag
                else:
                    sped += mag
        ncfn = iemre.get_hourly_ncname(sts.year)
        if os.path.isfile(ncfn):
            with ncopen(ncfn, timeout=600) as hnc:
                phour += np.sum(hnc.variables["p01m"][offset1:, :, :], 0)
                for offset in range(offset1, hnc.dimensions["time"].size):
                    uwnd = hnc.variables["uwnd"][offset, :, :]
                    vwnd = hnc.variables["vwnd"][offset, :, :]
                    if uwnd.mask.all():
                        LOG.warning("No wind for offset: %s", offset)
                        continue
                    windhours += 1
                    sped += (uwnd**2 + vwnd**2) ** 0.5
    else:
        ncfn = iemre.get_hourly_ncname(sts.year)
        if not os.path.isfile(ncfn):
            LOG.warning("Missing %s", ncfn)
            return
        with ncopen(ncfn, timeout=600) as hnc:
            phour = np.sum(hnc.variables["p01m"][offset1:offset2, :, :], 0)
            sped = None
            for offset in range(offset1, offset2):
                uwnd = hnc.variables["uwnd"][offset, :, :]
                vwnd = hnc.variables["vwnd"][offset, :, :]
                if uwnd.mask.all():
                    # Quell logging when we are close to current clock time.
                    now = sts + datetime.timedelta(hours=offset - offset1)
                    if now < (utc() - datetime.timedelta(hours=3)):
                        LOG.warning(
                            "No wind for offset: %s[%s-%s] %s",
                            offset,
                            offset1,
                            offset2,
                            now,
                        )
                    continue
                windhours += 1
                mag = (uwnd**2 + vwnd**2) ** 0.5
                if sped is None:
                    sped = mag
                else:
                    sped += mag
    ds["p01d"].values = np.where(phour < 0, 0, phour)
    if windhours > 0:
        ds["wind_speed"].values = sped / windhours


def do_precip12(ts, ds):
    """Compute the 24 Hour precip at 12 UTC, we do some more tricks though"""
    offset = iemre.daily_offset(ts)
    ets = utc(ts.year, ts.month, ts.day, 12)
    sts = ets - datetime.timedelta(hours=24)
    offset1 = iemre.hourly_offset(sts)
    offset2 = iemre.hourly_offset(ets)
    if ts.month == 1 and ts.day == 1:
        if sts.year >= 1900:
            LOG.warning(
                "p01d_12z  for %s [idx:%s] %s(%s)->%s(%s) SPECIAL",
                ts,
                offset,
                sts.strftime("%Y%m%d%H"),
                offset1,
                ets.strftime("%Y%m%d%H"),
                offset2,
            )
        ncfn = iemre.get_hourly_ncname(ets.year)
        if not os.path.isfile(ncfn):
            LOG.warning("Missing %s", ncfn)
            return
        with ncopen(ncfn, timeout=600) as hnc:
            phour = np.sum(hnc.variables["p01m"][:offset2, :, :], 0)
        with ncopen(iemre.get_hourly_ncname(sts.year), timeout=600) as hnc:
            phour += np.sum(hnc.variables["p01m"][offset1:, :, :], 0)
    else:
        ncfn = iemre.get_hourly_ncname(ts.year)
        if not os.path.isfile(ncfn):
            LOG.warning("Missing %s", ncfn)
            return
        with ncopen(ncfn, timeout=600) as hnc:
            phour = np.sum(hnc.variables["p01m"][offset1:offset2, :, :], 0)
    ds["p01d_12z"].values = np.where(phour < 0, 0, phour)


def grid_day12(ts, ds):
    """Use the COOP data for gridding"""
    LOG.info("12z hi/lo for %s", ts)
    mybuf = 2.0
    # non-midwest COOP ingest is not "complete" until start of 2012
    if ts.year > 2011:
        df = read_sql(
            f"""
           SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat, s.state,
           s.id as station, s.name as name,
           (CASE WHEN pday >= 0 then pday else null end) as precipdata,
           (CASE WHEN snow >= 0 then snow else null end) as snowdata,
           (CASE WHEN snowd >= 0 then snowd else null end) as snowddata,
           (CASE WHEN max_tmpf > -50 and max_tmpf < 130
               then max_tmpf else null end) as highdata,
           (CASE WHEN min_tmpf > -50 and min_tmpf < 95
               then min_tmpf else null end) as lowdata
           from summary_{ts.year} c, stations s WHERE day = %s and
           ST_Contains(
  ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s  %s, %s %s, %s %s, %s %s))'),
  geom) and s.network ~* 'COOP' and c.iemid = s.iemid and
  extract(hour from c.coop_valid at time zone s.tzname) between 4 and 11
            """,
            PGCONN,
            params=(
                ts,
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
            ),
        )
        LOG.info("loaded %s rows from iemaccess database", len(df.index))
    else:
        df = read_sql(
            """
        WITH mystations as (
            SELECT id, ST_X(geom) as lon, ST_Y(geom) as lat, state, name
            from stations where ST_Contains(
  ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s  %s, %s %s, %s %s, %s %s))'),
  geom) and network ~* 'CLIMATE' and substr(id, 3, 1) not in ('C', 'D', 'T')
            and substr(id, 3, 4) != '0000'
        )
        SELECT m.lon, m.lat, m.state, m.id as station, m.name as name,
        case when (precip_estimated or precip_hour is null or
            precip_hour < 4 or precip_hour > 11) then null
            else precip end as precipdata,
        snow as snowdata, snowd as snowddata,
        case when (temp_estimated or temp_hour is null or temp_hour < 4
            or temp_hour > 11) then null else high end as highdata,
        case when (temp_estimated or temp_hour is null or temp_hour < 4
            or temp_hour > 11) then null else low end as lowdata
        from alldata a JOIN mystations m
        ON (a.station = m.id) WHERE a.day = %s
        """,
            COOP_PGCONN,
            params=(
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
                ts,
            ),
        )
        LOG.info("loaded %s rows from climodat database", len(df.index))
    # Require that high > low before any gridding, accounts for some COOP
    # sites that only report TOB and not 24 hour high/low
    df.loc[df["highdata"] <= df["lowdata"], ["highdata", "lowdata"]] = None

    if len(df.index) > 4:
        res = generic_gridder(df, "highdata")
        ds["high_tmpk_12z"].values = convert_value(res, "degF", "degK")

        res = generic_gridder(df, "lowdata")
        ds["low_tmpk_12z"].values = convert_value(res, "degF", "degK")

        res = generic_gridder(df, "snowdata")
        ds["snow_12z"].values = convert_value(res, "inch", "millimeter")

        res = generic_gridder(df, "snowddata")
        ds["snowd_12z"].values = convert_value(res, "inch", "millimeter")
    else:
        LOG.warning(
            "%s has %02i entries, FAIL", ts.strftime("%Y-%m-%d"), len(df.index)
        )


def grid_day(ts, ds):
    """Do our gridding"""
    mybuf = 2.0
    if ts.year > 1927:
        df = read_sql(
            f"""
           SELECT ST_x(s.geom) as lon, ST_y(s.geom) as lat, s.state,
           s.name, s.id as station,
           (CASE WHEN pday >= 0 then pday else null end) as precipdata,
           (CASE WHEN max_tmpf > -50 and max_tmpf < 130
               then max_tmpf else null end) as highdata,
           (CASE WHEN min_tmpf > -50 and min_tmpf < 95
               then min_tmpf else null end) as lowdata,
           (CASE WHEN max_dwpf > -50 and max_dwpf < 130
               then max_dwpf else null end) as highdwpf,
           (CASE WHEN min_dwpf > -50 and min_dwpf < 95
               then min_dwpf else null end) as lowdwpf,
            (CASE WHEN min_rh > 0 and min_rh < 101
             then min_rh else null end) as minrh,
            (CASE WHEN max_rh > 0 and max_rh < 101
             then max_rh else null end) as maxrh
           from summary_{ts.year} c, stations s WHERE day = %s and
           ST_Contains(
  ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s  %s, %s %s, %s %s, %s %s))'),
  geom) and s.network ~* 'ASOS' and c.iemid = s.iemid
            """,
            PGCONN,
            params=(
                ts,
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
            ),
        )
    else:
        df = read_sql(
            """
        WITH mystations as (
            SELECT id, ST_X(geom) as lon, ST_Y(geom) as lat, state, name
            from stations where ST_Contains(
  ST_GeomFromEWKT('SRID=4326;POLYGON((%s %s, %s  %s, %s %s, %s %s, %s %s))'),
  geom) and network ~* 'CLIMATE' and (temp24_hour is null or
            temp24_hour between 4 and 10)
            and substr(id, 3, 1) not in ('C', 'D', 'T')
            and substr(id, 3, 4) != '0000'
        )
        SELECT m.lon, m.lat, m.state, m.id as station, m.name as name,
        precip as precipdata, snow as snowdata, snowd as snowddata,
        high as highdata, low as lowdata,
        null as highdwpf, null as lowdwpf,
        null as minrh, null as maxrh
        from alldata a JOIN mystations m
        ON (a.station = m.id) WHERE a.day = %s
        """,
            COOP_PGCONN,
            params=(
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.NORTH + mybuf,
                iemre.EAST + mybuf,
                iemre.SOUTH - mybuf,
                iemre.WEST - mybuf,
                iemre.SOUTH - mybuf,
                ts,
            ),
        )
    if len(df.index) < 4:
        LOG.warning(
            "%s has %02i entries, FAIL", ts.strftime("%Y-%m-%d"), len(df.index)
        )
        return
    res = generic_gridder(df, "highdata")
    ds["high_tmpk"].values = convert_value(res, "degF", "degK")
    res = generic_gridder(df, "lowdata")
    ds["low_tmpk"].values = convert_value(res, "degF", "degK")
    hres = generic_gridder(df, "highdwpf")
    lres = generic_gridder(df, "lowdwpf")
    if hres is not None and lres is not None:
        ds["avg_dwpk"].values = convert_value(
            (hres + lres) / 2.0, "degF", "degK"
        )
    res = generic_gridder(df, "minrh")
    if res is not None:
        ds["min_rh"].values = res
    res = generic_gridder(df, "maxrh")
    if res is not None:
        ds["max_rh"].values = res


def workflow(ts, irealtime, justprecip):
    """Do Work"""
    LOG.info("Run %s irealtime: %s justprecip: %s", ts, irealtime, justprecip)
    # load up our current data
    ds = iemre.get_grids(ts)
    LOG.info("loaded %s variables from IEMRE database", len(ds))
    # For this date, the 12 UTC COOP obs will match the date
    if not justprecip:
        LOG.info("doing 12z logic for %s", ts)
        grid_day12(ts, ds)
    do_precip12(ts, ds)
    # This is actually yesterday!
    if irealtime:
        iemre.set_grids(ts, ds)
        subprocess.call(f"python db_to_netcdf.py {ts:%Y %m %d}", shell=True)
        ts -= datetime.timedelta(days=1)
        ds = iemre.get_grids(ts)
    if not justprecip:
        LOG.info("doing calendar day logic for %s", ts)
        grid_day(ts, ds)
    copy_iemre(ts, ds)
    LOG.info("calling iemre.set_grids()")
    iemre.set_grids(ts, ds)
    subprocess.call(f"python db_to_netcdf.py {ts:%Y %m %d}", shell=True)


def main(argv):
    """Go Main Go"""
    if len(argv) >= 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        # specify any fifth argument to turn off non-precip gridding
        workflow(ts, False, len(argv) == 5)
    else:
        ts = datetime.date.today()
        workflow(ts, True, False)


if __name__ == "__main__":
    main(sys.argv)
