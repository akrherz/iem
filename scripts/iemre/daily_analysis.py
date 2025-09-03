"""Grid the daily/24H data onto a grid for IEMRE

This is tricky as some variables we can compute sooner than others.

    RUN_MIDNIGHT.sh
    RUN_NOON.sh
    RUN_0Z.sh
    RUN_10_AFTER.sh
"""

import subprocess
from datetime import date, datetime, timedelta, timezone
from typing import cast

import click
import numpy as np
import pandas as pd
from metpy.calc import relative_humidity_from_dewpoint
from metpy.interpolate import inverse_distance_to_grid
from metpy.units import units
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.grid.nav import get_nav
from pyiem.grid.util import grid_smear
from pyiem.iemre import (
    DOMAINS,
    get_grids,
    get_hourly_ncname,
    hourly_offset,
    set_grids,
)
from pyiem.util import convert_value, logger, ncopen
from scipy.stats import zscore

LOG = logger()


def generic_gridder(df, idx, domain: str):
    """
    Generic gridding algorithm for easy variables
    """
    gridnav = get_nav("iemre", domain)
    if not idx.startswith("precip"):
        window = 2.0
        f1 = df[df[idx].notnull()]
        for lat in np.arange(gridnav.bottom, gridnav.top, window):
            for lon in np.arange(gridnav.left, gridnav.right, window):
                (west, east, south, north) = (
                    lon,
                    lon + window,
                    lat,
                    lat + window,
                )
                box = f1[
                    (f1["lat"] >= south)
                    & (f1["lat"] < north)
                    & (f1["lon"] >= west)
                    & (f1["lon"] < east)
                ]
                # can't QC data that is all equal
                if len(box.index) < 4 or box[idx].min() == box[idx].max():
                    continue
                z = np.abs(cast("np.ndarray", zscore(box[idx])))
                # Compute where the standard dev is +/- 2std
                bad = box[z > 1.5]
                df.loc[bad.index, idx] = np.nan

    df2 = df[df[idx].notnull()]
    if len(df2.index) < 4:
        LOG.info("Not enough data %s", idx)
        return None
    xi, yi = np.meshgrid(gridnav.x_points, gridnav.y_points)
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


def compute_daily_pairs(
    dt: date, domain: str, is_12z: bool
) -> list[tuple[datetime, datetime]]:
    """Figure out the pairs.

    The 12z variant is a bit different and will include the end timestamp
    """
    # Compute a timestamp at noon within the local calendar date
    noon_local = datetime(
        dt.year, dt.month, dt.day, 12, tzinfo=DOMAINS[domain]["tzinfo"]
    )
    if is_12z:
        ets = noon_local.replace(hour=7)
        sts = ets - timedelta(hours=23)
    else:
        sts = noon_local.replace(hour=1 if noon_local.dst() else 0)
        ets = sts + timedelta(hours=23)
    # Logic below needs UTC
    sts = sts.astimezone(timezone.utc)
    ets = ets.astimezone(timezone.utc)
    LOG.info("Using %s to %s for %s[is_12z: %s]", sts, ets, domain, is_12z)
    pairs = [(sts, ets)]
    if sts.year != ets.year:
        # These are inclusive
        pairs = [
            (sts, sts.replace(hour=23)),
            (ets.replace(hour=0), ets),
        ]
    return pairs


def copy_iemre_hourly(ts: date, ds, domain: str):
    """Lots of work to do here..."""
    pairs = compute_daily_pairs(ts, domain, is_12z=False)
    pairs12z = compute_daily_pairs(ts, domain, is_12z=True)

    # One Off
    for vname in ["min_rh", "max_rh"]:
        aggfunc = np.ma.max if vname == "max_rh" else np.ma.min
        res = None
        for pair in pairs:
            ncfn = get_hourly_ncname(pair[0].year, domain)
            tidx1 = hourly_offset(pair[0])
            tidx2 = hourly_offset(pair[1])
            with ncopen(ncfn, timeout=600) as nc:
                tmpk = nc.variables["tmpk"]
                dwpk = nc.variables["dwpk"]
                for offset in range(tidx1, tidx2 + 1):
                    rh = (
                        relative_humidity_from_dewpoint(
                            units("degK") * tmpk[offset],
                            units("degK") * dwpk[offset],
                        ).m
                        * 100.0
                    )
                    if res is None:
                        res = rh
                    else:
                        res = aggfunc([res, rh], axis=0)
        ds[vname].values = res

    # One off
    hours = 0
    runningsum = None
    for pair in pairs:
        ncfn = get_hourly_ncname(pair[0].year, domain)
        tidx1 = hourly_offset(pair[0])
        tidx2 = hourly_offset(pair[1])
        with ncopen(ncfn, timeout=600) as nc:
            uwnd = nc.variables["uwnd"]
            vwnd = nc.variables["vwnd"]
            for offset in range(tidx1, tidx2 + 1):
                # Skip this offset if values are all masked
                if uwnd[offset].mask.all() or vwnd[offset].mask.all():
                    LOG.info("Skipping masked wind data at %s", offset)
                    continue
                # Assuming zeros, I think was a bad life choice
                val = np.hypot(uwnd[offset], vwnd[offset])
                if runningsum is None:
                    runningsum = val
                else:
                    runningsum += val
                if np.nanmax(val) > 0:
                    hours += 1
    if hours > 0:
        ds["wind_speed"].values = runningsum / hours
    # -----------------------------------------------------------------
    for vname in (
        "high_tmpk low_tmpk p01d high_soil4t avg_dwpk rsds "
        "low_soil4t high_tmpk_12z low_tmpk_12z p01d_12z"
    ).split():
        if vname == "rsds" and domain == "":
            # Done via other means
            continue
        res = None
        aggfunc = np.ma.max
        if vname in ["p01d_12z", "p01d", "rsds"]:
            aggfunc = np.ma.sum  # was np.nansum, better check this
        elif vname.startswith("low"):
            aggfunc = np.ma.min
        elif vname.startswith("avg"):
            aggfunc = np.ma.mean
        ncvarname = (
            vname.replace("high_", "")
            .replace("low_", "")
            .replace("_12z", "")
            .replace("avg_", "")
        )
        ncvarname = "p01m" if ncvarname == "p01d" else ncvarname
        for pair in pairs12z if vname.endswith("12z") else pairs:
            ncfn = get_hourly_ncname(pair[0].year, domain)
            tidx1 = hourly_offset(pair[0])
            tidx2 = hourly_offset(pair[1])
            tslice = slice(tidx1, tidx2 + 1)
            if vname.startswith("p01d"):
                # Caution: precip is stored arrears, so we have ugliness
                tslice = slice(0 if tidx1 == 0 else tidx1 + 1, tidx2 + 2)
            LOG.info("Using %s[%s] for %s", ncfn, tslice, vname)
            with ncopen(ncfn, timeout=600) as nc:
                ncvar = nc.variables[ncvarname]
                ncval = aggfunc(ncvar[tslice], axis=0)
                if res is None:
                    res = ncval
                else:
                    res = aggfunc([res, ncval], axis=0)
        # NB: these are crude bias offsets involved when using hourly data
        if vname in ["high_tmpk", "high_tmpk_12z"]:
            res += 0.8
        if vname in ["low_tmpk", "low_tmpk_12z"]:
            res -= 0.8
        if vname == "rsds":
            # Convert from Wm-2
            res = res / 24.0
        ds[vname].values = res


def use_climodat_12z(ts, ds):
    """Look at what we have in climodat."""
    mybuf = 2
    gridnav = get_nav("iemre", "")
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        WITH mystations as (
            SELECT id, ST_X(geom) as lon, ST_Y(geom) as lat, state, name
            from stations where ST_Contains(
            ST_MakeEnvelope(:west, :south, :east, :north, 4326), geom) and
            network ~* 'CLIMATE' and substr(id, 3, 1) not in ('C', 'D', 'T')
            and substr(id, 3, 4) != '0000'
        )
        SELECT m.lon, m.lat, m.state, m.id as station, m.name as name,
        case when (precip_estimated or precip_hour is null or
            precip_hour < 4 or precip_hour > 11) then null
            else precip end as precipdata,
        snow as snowdata, snowd as snowddata,
        case when temp_estimated then null else high end as highdata_all,
        case when temp_estimated then null else low end as lowdata_all
        from alldata a JOIN mystations m
        ON (a.station = m.id) WHERE a.day = :ts
        """),
            conn,
            params={
                "west": gridnav.left - mybuf,
                "south": gridnav.bottom - mybuf,
                "east": gridnav.right + mybuf,
                "north": gridnav.top + mybuf,
                "ts": ts,
            },
        )
    LOG.info("loaded %s rows from climodat database", len(df.index))
    if len(df.index) < 50:
        if ts != date.today():
            LOG.warning("Failed quorum")
        return
    if ts.year < 1951:
        res = generic_gridder(df, "highdata_all", "")
        ds["high_tmpk_12z"].values = convert_value(res, "degF", "degK")

        res = generic_gridder(df, "lowdata_all", "")
        ds["low_tmpk_12z"].values = convert_value(res, "degF", "degK")

    res = generic_gridder(df, "snowdata", "")
    if res is not None and ts < date(2008, 10, 1):  # NOHRSC covers
        ds["snow_12z"].values = convert_value(res, "inch", "millimeter")

    res = generic_gridder(df, "snowddata", "")
    if res is not None:
        ds["snowd_12z"].values = convert_value(res, "inch", "millimeter")


def use_asos_daily(ts, ds, domain):
    """Grid out available ASOS data."""
    mybuf = 2.0
    gridnav = get_nav("iemre", domain)
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper(
                """
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
           from {table} c, stations s WHERE day = :ts and
           ST_Contains(ST_MakeEnvelope(:west, :south, :east, :north, 4326),
           geom) and s.network ~* 'ASOS'
           and c.iemid = s.iemid
            """,
                table=f"summary_{ts:%Y}",
            ),
            conn,
            params={
                "west": gridnav.left - mybuf,
                "south": gridnav.bottom - mybuf,
                "east": gridnav.right + mybuf,
                "north": gridnav.top + mybuf,
                "ts": ts,
            },
        )
    if len(df.index) < 4:
        LOG.warning("Failed data quorum")
        return
    if len(df.index) > 300:
        LOG.info("Using ASOS for high/low")
        res = generic_gridder(df, "highdata", domain)
        ds["high_tmpk"].values = convert_value(res, "degF", "degK")
        res = generic_gridder(df, "lowdata", domain)
        ds["low_tmpk"].values = convert_value(res, "degF", "degK")

    # We have alternative
    hres = generic_gridder(df, "highdwpf", domain)
    lres = generic_gridder(df, "lowdwpf", domain)
    if hres is not None and lres is not None:
        ds["avg_dwpk"].values = convert_value(
            (hres + lres) / 2.0, "degF", "degK"
        )
    res = generic_gridder(df, "minrh", domain)
    if res is not None:
        ds["min_rh"].values = res
    res = generic_gridder(df, "maxrh", domain)
    if res is not None:
        ds["max_rh"].values = res


def use_climodat_daily(ts: date, ds):
    """Do our gridding"""
    mybuf = 2.0
    gridnav = get_nav("iemre", "")
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper("""
        WITH mystations as (
            SELECT id, ST_X(geom) as lon, ST_Y(geom) as lat, state, name
            from stations where ST_Contains(
            ST_MakeEnvelope(:west, :south, :east, :north, 4326), geom) and
            network ~* 'CLIMATE' and substr(id, 3, 1) not in ('C', 'D', 'T')
            and substr(id, 3, 4) != '0000'
        )
        SELECT m.lon, m.lat, m.state, m.id as station, m.name as name,
        case when not temp_estimated then high else null end as highdata_all,
        case when not temp_estimated then low else null end as lowdata_all,
        case when not precip_estimated then precip else null end as
            precipdata_all,
        case when temp_estimated or temp_hour is null or high < -50 or
            high > 130 or (temp_hour > 4 and temp_hour < 13) then null
            else high end as highdata,
        case when temp_estimated or temp_hour is null or low < -90 or low > 90
            or (temp_hour > 4 and temp_hour < 13) then null else low end
            as lowdata,
        case when precip_estimated or precip_hour is null or
        (precip_hour > 4 and precip_hour < 13) then null else precip end
            as precipdata
        from alldata a JOIN mystations m
        ON (a.station = m.id) WHERE a.day = :ts
        """),
            conn,
            params={
                "west": gridnav.left - mybuf,
                "south": gridnav.bottom - mybuf,
                "east": gridnav.right + mybuf,
                "north": gridnav.top + mybuf,
                "ts": ts,
            },
        )
    if len(df.index) < 4:
        if ts != date.today():
            LOG.warning("Failed quorum")
        return
    suffix = "_all" if ts.year < 1951 else ""
    res = generic_gridder(df, f"highdata{suffix}", "")
    if res is not None:
        ds["high_tmpk"].values = convert_value(res, "degF", "degK")
    res = generic_gridder(df, f"lowdata{suffix}", "")
    if res is not None:
        ds["low_tmpk"].values = convert_value(res, "degF", "degK")
    res = generic_gridder(df, f"precipdata{suffix}", "")
    if res is not None:
        ds["p01d"].values = convert_value(res, "inch", "mm")


def workflow(ts: date, domain: str):
    """Do Work"""
    # load up our current data
    ds = get_grids(ts, domain=domain)
    LOG.info("loaded %s variables from IEMRE database", len(ds))

    # rsds -> grid_rsds.py
    # power_swdn -> TODO

    # high_tmpk, low_tmpk, p01d, wind_speed, min_rh, max_rh, high_soil4t,
    # low_soil4t, high_tmpk_12z low_tmpk_12z p01d_12z
    if ts.year > 1949:
        copy_iemre_hourly(ts, ds, domain)
    else:
        # While data does exist, we have practical availability issues
        if ts.year > 1940:
            LOG.info("Using ASOS for daily summary variables")
            use_asos_daily(ts, ds, domain)
        if domain == "":
            use_climodat_daily(ts, ds)

    if domain == "":
        # snow_12z snowd_12z
        use_climodat_12z(ts, ds)

    for vname in list(ds.keys()):
        # Some grids are too tight to the CONUS boundary, so we smear things
        # out some.
        vals = ds[vname].to_masked_array()
        vals = grid_smear(vals, shift=4)
        ds[vname].values = vals
        msg = f"{vname:14s} {ds[vname].min():6.2f} {ds[vname].max():6.2f}"
        LOG.info(msg)
    set_grids(ts, ds, domain=domain)
    subprocess.call(
        [
            "python",
            "db_to_netcdf.py",
            f"--date={ts:%Y-%m-%d}",
            f"--domain={domain}",
        ]
    )


@click.command()
@click.option(
    "--date", "valid", type=click.DateTime(), help="Date", required=True
)
@click.option("--domain", default="", help="Domain to process", type=str)
def main(valid: datetime, domain: str):
    """Go Main Go"""
    dt = valid.date()
    LOG.info("Run %s for domain: '%s'", dt, domain)
    workflow(dt, domain)
    LOG.info("Done.")


if __name__ == "__main__":
    main()
