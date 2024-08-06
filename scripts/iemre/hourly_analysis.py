"""I produce the hourly analysis used by IEMRE.

Run from RUN_10_AFTER.sh
"""

import datetime
import os
import warnings

import click
import numpy as np
import pandas as pd
import pint
import pygrib
from affine import Affine
from metpy.calc import wind_components
from metpy.interpolate import inverse_distance_to_grid
from metpy.units import masked_array, units
from pyiem import iemre
from pyiem.database import get_sqlalchemy_conn
from pyiem.iemre import grb2iemre, hourly_offset, reproject2iemre
from pyiem.util import archive_fetch, logger, ncopen
from sqlalchemy import text

# Prevent invalid value encountered in cast
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()
MEMORY = {"ts": datetime.datetime.now()}


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
    try:
        with ncopen(ncfn) as nc:
            lats = nc.variables["lat"][:]
            lons = nc.variables["lon"][:]
            aff = Affine(
                lons[1] - lons[0],
                0,
                lons[0],
                0,
                lats[1] - lats[0],
                lats[0],
            )
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
                for shift in (-4, 4):
                    for axis in (0, 1):
                        vals_shifted = np.roll(vals, shift=shift, axis=axis)
                        idx = ~vals_shifted.mask * vals.mask
                        vals[idx] = vals_shifted[idx]
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
        fn = (ts - datetime.timedelta(hours=offset)).strftime(
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
                grb = grbs.select(shortName=task)[0]
                res.append(grb2iemre(grb))
            return res[0] if len(res) == 1 else res
        except Exception as exp:
            LOG.info("%s exp:%s for %s", fn, exp, kind)
        finally:
            grbs.close()
    return None


def grid_wind(df, hasdata, domain):
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
    ugrid = generic_gridder(df, "u", hasdata, applymask=False, domain=domain)
    vgrid = generic_gridder(df, "v", hasdata, applymask=False, domain=domain)
    return ugrid, vgrid


def grid_skyc(df, hasdata, domain):
    """Take the max sky coverage value."""
    cols = ["max_skyc1", "max_skyc2", "max_skyc3", "max_skyc4"]
    df["skyc"] = df[cols].max(axis="columns")
    return generic_gridder(df, "skyc", hasdata, domain=domain)


def generic_gridder(df, idx, hasdata, applymask=True, domain=""):
    """Generic gridding algorithm for easy variables"""
    dom = iemre.DOMAINS[domain]
    df2 = df[pd.notnull(df[idx])]
    xi, yi = np.meshgrid(
        np.arange(dom["west"], dom["east"], iemre.DX),
        np.arange(dom["south"], dom["north"], iemre.DY),
    )
    res = np.ones(xi.shape) * np.nan
    # set a sentinel of where we won't be estimating
    if applymask:
        res = np.where(hasdata > 0, res, -9999)
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


def grid_hour(ts, domain):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    LOG.info("Processing %s", ts)
    with ncopen(iemre.get_hourly_ncname(ts.year), "r", timeout=300) as nc:
        hasdata = nc.variables["hasdata"][:, :]
    ts0 = ts - datetime.timedelta(minutes=10)
    ts1 = ts + datetime.timedelta(minutes=10)

    mybuf = 2.0
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text("""SELECT station, ST_x(geom) as lon, st_y(geom) as lat,
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
                "west": iemre.WEST - mybuf,
                "south": iemre.SOUTH - mybuf,
                "east": iemre.EAST + mybuf,
                "north": iemre.NORTH + mybuf,
                "ts0": ts0,
                "ts1": ts1,
            },
            index_col="station",
        )

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
        ures, vres = grid_wind(df, hasdata, domain)
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
        tmpf = generic_gridder(df, "max_tmpf", hasdata, domain=domain)

    # only use RTMA if tmp worked
    res = None
    if tmp_used_rtma:
        res = use_rtma(ts, "dwp")
    if res is None:
        # try ERA5Land
        res = use_era5land(ts, "dwpk", domain)
    # Ensure we have RTMA temps available
    if not did_gridding and res is not None:
        dwpf = masked_array(res, data_units="degK").to("degF").m
    else:
        if df.empty:
            LOG.warning("%s has no entries, FAIL", ts)
            return
        dwpf = generic_gridder(df, "max_dwpf", hasdata, domain=domain)

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
    res = grid_skyc(df, hasdata, domain)
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
    offset = iemre.hourly_offset(valid)
    with ncopen(
        iemre.get_hourly_ncname(valid.year, domain), "a", timeout=300
    ) as nc:
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
def main(valid, domain):
    """Go Main"""
    grid_hour(valid.replace(tzinfo=datetime.timezone.utc), domain)


if __name__ == "__main__":
    main()
