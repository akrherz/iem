"""I produce the hourly analysis used by IEMRE.

Run from RUN_10_AFTER.sh
"""

import os
import warnings
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pandas as pd
import pint
import pygrib
from metpy.calc import wind_components
from metpy.interpolate import inverse_distance_to_grid
from metpy.units import masked_array, units
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.grid.nav import get_nav
from pyiem.grid.util import grid_smear
from pyiem.iemre import (
    get_hourly_ncname,
    grb2iemre,
    hourly_offset,
    reproject2iemre,
)
from pyiem.util import archive_fetch, logger, ncopen

# Prevent invalid value encountered in cast
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()
MEMORY = {"ts": datetime.now()}


def use_era5land(ts, kind, domain):
    """Use the ERA5Land dataset."""
    tasks = {
        "wind": ["uwnd", "vwnd"],
    }
    dd = "" if domain == "" else f"_{domain}"
    ncfn = f"/mesonet/data/era5{dd}/{ts:%Y}_era5land_hourly.nc"
    if not os.path.isfile(ncfn):
        LOG.warning("Failed to find %s", ncfn)
        return None
    tidx = hourly_offset(ts)
    aff = get_nav("era5land", domain).affine
    try:
        with ncopen(ncfn) as nc:
            res = []
            for task in tasks.get(kind, [kind]):
                if task == "soilt":
                    vals = nc.variables[task][tidx, 0, :, :]
                else:
                    vals = nc.variables[task][tidx, :, :]
                if vals.mask.all():
                    continue
                # OK, ERA5Land is tight to land and when we interpolate
                # we end up with slivers of no data.  So we goose things
                # to smear data to the borders.
                vals = grid_smear(vals, shift=4)
                res.append(
                    reproject2iemre(
                        vals.filled(np.nan), aff, "epsg:4326", domain=domain
                    )
                )
        if res:
            LOG.info("found %s", kind)
            return res[0] if len(res) == 1 else res

    except Exception as exp:
        LOG.warning("%s exp:%s", ncfn, exp)
    LOG.info("returning None for %s", kind)
    return None


def use_hrrr_soilt(ts):
    """Verbatim copy HRRR, if it exists."""
    # We may be running close to real-time, so it makes some sense to take
    # files from the recent past.
    for offset in range(5):
        fn = (ts - timedelta(hours=offset)).strftime(
            "%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf00.grib2"
        )
        with archive_fetch(fn) as fn:
            if fn is None:
                continue
            try:
                grbs = pygrib.open(fn)
                for grb in grbs:
                    if (
                        grb.shortName != "st"
                        or str(grb).find("level 0.1 m") == -1
                    ):
                        continue
                    return grb2iemre(grb)
                grbs.close()
            except Exception as exp:
                LOG.info("%s exp:%s", fn, exp)
    return None


def use_rtma(ts, kind):
    """Verbatim copy RTMA, if it exists."""
    if ts.year < 2011:
        return None
    ppath = ts.strftime("%Y/%m/%d/model/rtma/%H/rtma.t%Hz.awp2p5f000.grib2")
    with archive_fetch(ppath) as fn:
        if fn is None:
            return None
        tasks = {
            "wind": [
                "10u",
                "10v",
            ],
            "tmp": [
                "2t",
            ],
            "dwp": [
                "2d",
            ],
        }
        res = []
        try:
            grbs = pygrib.open(fn)
            for task in tasks[kind]:
                grb = grbs.select(shortName=task, typeOfGeneratingProcess=0)[0]
                res.append(grb2iemre(grb))
            return res[0] if len(res) == 1 else res
        except Exception as exp:
            LOG.info("%s exp:%s for %s", fn, exp, kind)
        finally:
            grbs.close()
    return None


def grid_wind(df, domain):
    """
    Grid winds based on u and v components
    @return uwnd, vwnd
    """
    # compute components
    u = []
    v = []
    for _station, row in df.iterrows():
        (_u, _v) = wind_components(
            units("knot") * row["sknt"], units("degree") * row["drct"]
        )
        u.append(_u.to("meter / second").m)
        v.append(_v.to("meter / second").m)
    df["u"] = u
    df["v"] = v
    ugrid = generic_gridder(df, "u", domain=domain)
    vgrid = generic_gridder(df, "v", domain=domain)
    return ugrid, vgrid


def grid_skyc(df, domain):
    """Take the max sky coverage value."""
    cols = ["max_skyc1", "max_skyc2", "max_skyc3", "max_skyc4"]
    df["skyc"] = df[cols].max(axis="columns")
    return generic_gridder(df, "skyc", domain=domain)


def generic_gridder(df, idx, domain=""):
    """Generic gridding algorithm for easy variables"""
    gridnav = get_nav("iemre", domain)
    df2 = df[pd.notnull(df[idx])]
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
    # replace sentinel back to np.nan
    res = np.where(res == -9999, np.nan, res)
    return np.ma.array(res, mask=np.isnan(res))


def grid_hour(ts: datetime, domain: str):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    LOG.info("Processing %s", ts)
    ts0 = ts - timedelta(minutes=10)
    ts1 = ts + timedelta(minutes=10)

    mybuf = 2.0
    gridnav = get_nav("iemre", domain)
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            sql_helper("""SELECT station, ST_x(geom) as lon, st_y(geom) as lat,
    max(case when tmpf > -60 and tmpf < 130 THEN tmpf else null end)
        as max_tmpf,
    max(case when sknt > 0 and sknt < 100 then sknt else 0 end) as max_sknt,
    max(getskyc(skyc1)) as max_skyc1,
    max(getskyc(skyc2)) as max_skyc2,
    max(getskyc(skyc3)) as max_skyc3,
    max(getskyc(skyc4)) as max_skyc4,
    max(case when p01i > 0 and p01i < 1000 then p01i else 0 end) as phour,
    max(case when dwpf > -60 and dwpf < 100 THEN dwpf else null end)
        as max_dwpf,
    max(case when sknt >= 0 then sknt else 0 end) as sknt,
    max(case when sknt >= 0 then drct else 0 end) as drct
    from alldata a JOIN stations t on (a.station = t.id) WHERE
    ST_Contains(ST_MakeEnvelope(:west, :south, :east, :north, 4326), geom)
    and t.network ~* 'ASOS' and
    valid >= :ts0 and valid < :ts1 and report_type != 1
    GROUP by station, lon, lat"""),
            conn,
            params={
                "west": gridnav.left - mybuf,
                "south": gridnav.bottom - mybuf,
                "east": gridnav.right + mybuf,
                "north": gridnav.top + mybuf,
                "ts0": ts0,
                "ts1": ts1,
            },
            index_col="station",
        )

    # RSDS
    res = use_era5land(ts, "rsds", domain)
    if res is not None:
        write_grid(ts, "rsds", res, domain)

    # Soil Temperature, try ERA5Land
    res = use_era5land(ts, "soilt", domain)
    if res is None and domain == "":
        # Use HRRR
        res = use_hrrr_soilt(ts)
    if res is not None:
        write_grid(ts, "soil4t", res, domain)

    # try first to use RTMA
    res = None
    if domain == "":
        res = use_rtma(ts, "wind")
    if res is None:
        # try ERA5Land
        res = use_era5land(ts, "wind", domain)
    if res is not None:
        ures, vres = res
    else:
        if df.empty:
            LOG.warning("%s has no entries, FAIL", ts)
            return
        ures, vres = grid_wind(df, domain)
    if ures is None:
        LOG.warning("Failure for uwnd at %s", ts)
    else:
        write_grid(ts, "uwnd", ures, domain)
        write_grid(ts, "vwnd", vres, domain)

    # try first to use RTMA
    res = None
    if domain == "":
        res = use_rtma(ts, "tmp")
    tmp_used_rtma = res is not None
    if res is None:
        # try ERA5Land
        res = use_era5land(ts, "tmpk", domain)
    did_gridding = False
    if res is not None:
        tmpf = masked_array(res, data_units="degK").to("degF").m
    else:
        if df.empty:
            LOG.warning("%s has no entries, FAIL", ts)
            return
        did_gridding = True
        tmpf = generic_gridder(df, "max_tmpf", domain=domain)

    # only use RTMA if tmp worked
    res = None
    if tmp_used_rtma:
        res = use_rtma(ts, "dwp")
    if res is None:
        # try ERA5Land
        res = use_era5land(ts, "dwpk", domain)
        if res is not None and tmp_used_rtma:
            LOG.info("Forcing ERA5Land temperature, since dewpoint used it")
            tmpf = (
                masked_array(
                    use_era5land(ts, "tmpk", domain), data_units="degK"
                )
                .to("degF")
                .m
            )
    # Ensure we have RTMA temps available
    if not did_gridding and res is not None:
        dwpf = masked_array(res, data_units="degK").to("degF").m
    else:
        if df.empty:
            LOG.warning("%s has no entries, FAIL", ts)
            return
        dwpf = generic_gridder(df, "max_dwpf", domain=domain)

    # Only keep cases when tmpf >= dwpf and they are both not masked
    # Note some truncation issues here, so our comparison is not perfect
    idx = (tmpf >= (dwpf - 1)) & (~tmpf.mask) & (~dwpf.mask)
    dwpf[~idx] = np.nan
    tmpf[~idx] = np.nan

    write_grid(
        ts, "tmpk", masked_array(tmpf, data_units="degF").to("degK"), domain
    )
    write_grid(
        ts, "dwpk", masked_array(dwpf, data_units="degF").to("degK"), domain
    )
    res = grid_skyc(df, domain)
    if res is None:
        LOG.warning("No obs for skyc at %s", ts)
    else:
        write_grid(ts, "skyc", res, domain)


def write_grid(valid, vname, grid, domain):
    """Atomic write of data to our netcdf storage

    This is isolated so that we don't 'lock' up our file while intensive
    work is done
    """
    if isinstance(grid, pint.Quantity):
        grid = grid.m
    offset = hourly_offset(valid)
    with ncopen(get_hourly_ncname(valid.year, domain), "a", timeout=300) as nc:
        LOG.info(
            "offset: %s writing %s with min: %s max: %s Ames: %s",
            offset,
            vname,
            np.nanmin(grid),
            np.nanmax(grid),
            grid[151, 259],
        )
        nc.variables[vname][offset] = grid


@click.command()
@click.option("--valid", required=True, type=click.DateTime(), help="UTC")
@click.option("--domain", default="", help="Domain to process")
def main(valid: datetime, domain):
    """Go Main"""
    grid_hour(valid.replace(tzinfo=timezone.utc), domain)


if __name__ == "__main__":
    main()
