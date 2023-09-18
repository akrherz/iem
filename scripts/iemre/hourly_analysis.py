"""I produce the hourly analysis used by IEMRE.

Run from RUN_10_AFTER.sh
"""
import datetime
import os
import sys
import warnings

import numpy as np
import pandas as pd
import pygrib
from metpy.calc import wind_components
from metpy.interpolate import inverse_distance_to_grid
from metpy.units import masked_array, units
from pyiem import iemre
from pyiem.iemre import hourly_offset
from pyiem.util import get_sqlalchemy_conn, logger, ncopen, utc
from scipy.interpolate import NearestNDInterpolator, RegularGridInterpolator

# Prevent invalid value encountered in cast
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()
MEMORY = {"ts": datetime.datetime.now()}


def use_era5land(ts, kind):
    """Use the ERA5Land dataset."""
    tasks = {
        "wind": ["uwnd", "vwnd"],
        "soilt": ["soilt"],
    }
    ncfn = f"/mesonet/data/era5/{ts:%Y}_era5land_hourly.nc"
    if not os.path.isfile(ncfn):
        LOG.warning("Failed to find %s", ncfn)
        return None
    try:
        tidx = hourly_offset(ts)
        with ncopen(ncfn) as nc:
            lats = nc.variables["lat"][:]
            lons = nc.variables["lon"][:]
            res = []
            xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
            for task in tasks[kind]:
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
                nn = RegularGridInterpolator((lats, lons), vals.filled(np.nan))
                data = np.ma.array(nn((yi, xi)))
                data.mask = np.isnan(data)
                res.append(data)
        if res:
            return res[0] if len(res) == 1 else res

    except Exception as exp:
        LOG.warning("%s exp:%s", ncfn, exp)
    return None


def use_hrrr_soilt(ts):
    """Verbatim copy HRRR, if it exists."""
    # We may be running close to real-time, so it makes some sense to take
    # files from the recent past.
    grbfn = None
    for offset in range(5):
        fn = (ts - datetime.timedelta(hours=offset)).strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
            "hrrr.t%Hz.3kmf00.grib2"
        )
        if os.path.isfile(fn):
            grbfn = fn
            break
    if grbfn is None:
        LOG.info("Failed to find any HRRR grib files")
        return None
    try:
        grbs = pygrib.open(fn)
        lats = None
        for grb in grbs:
            if grb.shortName != "st" or str(grb).find("level 0.1 m") == -1:
                continue
            lats, lons = [np.ravel(x) for x in grb.latlons()]
            xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
            nn = NearestNDInterpolator((lons, lats), np.ravel(grb.values))
            return nn(xi, yi)
        grbs.close()
    except Exception as exp:
        LOG.debug("%s exp:%s", fn, exp)
    return None


def use_rtma(ts, kind):
    """Verbatim copy RTMA, if it exists."""
    fn = ts.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/rtma/%H/"
        "rtma.t%Hz.awp2p5f000.grib2"
    )
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
    if not os.path.isfile(fn):
        LOG.debug("Failed to find %s", fn)
        return None
    try:
        grbs = pygrib.open(fn)
        lats = None
        res = []
        for task in tasks[kind]:
            grb = grbs.select(shortName=task)[0]
            if lats is None:
                lats, lons = [np.ravel(x) for x in grb.latlons()]
            xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
            nn = NearestNDInterpolator((lons, lats), np.ravel(grb.values))
            res.append(nn(xi, yi))
        return res
    except Exception as exp:
        LOG.debug("%s exp:%s", fn, exp)
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
    ugrid = generic_gridder(df, "u", domain, applymask=False)
    vgrid = generic_gridder(df, "v", domain, applymask=False)
    return ugrid, vgrid


def grid_skyc(df, domain):
    """Take the max sky coverage value."""
    cols = ["max_skyc1", "max_skyc2", "max_skyc3", "max_skyc4"]
    df["skyc"] = df[cols].max(axis="columns")
    return generic_gridder(df, "skyc", domain)


def generic_gridder(df, idx, domain, applymask=True):
    """Generic gridding algorithm for easy variables"""
    df2 = df[pd.notnull(df[idx])]
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    res = np.ones(xi.shape) * np.nan
    # set a sentinel of where we won't be estimating
    if applymask:
        res = np.where(domain > 0, res, -9999)
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


def grid_hour(ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    LOG.info("Processing %s", ts)
    with ncopen(iemre.get_hourly_ncname(ts.year), "r", timeout=300) as nc:
        domain = nc.variables["hasdata"][:, :]
    ts0 = ts - datetime.timedelta(minutes=10)
    ts1 = ts + datetime.timedelta(minutes=10)

    mybuf = 2.0
    giswkt = "SRID=4326;POLYGON((%s %s, %s  %s, %s %s, %s %s, %s %s))" % (
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
    )
    params = (
        giswkt,
        ts0,
        ts1,
    )
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            """SELECT station, ST_x(geom) as lon, st_y(geom) as lat,
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
    ST_Contains(ST_GeomFromEWKT(%s), geom) and t.network ~* 'ASOS' and
    valid >= %s and valid < %s and report_type != 1
    GROUP by station, lon, lat""",
            conn,
            params=params,
            index_col="station",
        )

    # Soil Temperature, try ERA5Land
    res = use_era5land(ts, "soilt")
    if res is None:
        # Use HRRR
        res = use_hrrr_soilt(ts)
    if res is not None:
        write_grid(ts, "soil4t", res)

    # try first to use RTMA
    res = use_rtma(ts, "wind")
    if res is None:
        # try ERA5Land
        res = use_era5land(ts, "wind")
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
        write_grid(ts, "uwnd", ures)
        write_grid(ts, "vwnd", vres)

    # try first to use RTMA
    res = use_rtma(ts, "tmp")
    did_gridding = False
    if res is not None:
        tmpf = masked_array(res[0], data_units="degK").to("degF").m
    else:
        if df.empty:
            LOG.warning("%s has no entries, FAIL", ts)
            return
        did_gridding = True
        tmpf = generic_gridder(df, "max_tmpf", domain)

    # try first to use RTMA
    res = use_rtma(ts, "dwp")
    # Ensure we have RTMA temps available
    if not did_gridding and res is not None:
        dwpf = masked_array(res[0], data_units="degK").to("degF").m
    else:
        if df.empty:
            LOG.warning("%s has no entries, FAIL", ts)
            return
        dwpf = generic_gridder(df, "max_dwpf", domain)

    # require that dwpk <= tmpk
    mask = ~np.isnan(dwpf)
    mask[mask] &= dwpf[mask] > tmpf[mask]
    dwpf = np.where(mask, tmpf, dwpf)
    write_grid(ts, "tmpk", masked_array(tmpf, data_units="degF").to("degK"))
    write_grid(ts, "dwpk", masked_array(dwpf, data_units="degF").to("degK"))

    res = grid_skyc(df, domain)
    if res is None:
        LOG.warning("Failure for skyc at %s", ts)
    else:
        write_grid(ts, "skyc", res)


def write_grid(valid, vname, grid):
    """Atomic write of data to our netcdf storage

    This is isolated so that we don't 'lock' up our file while intensive
    work is done
    """
    offset = iemre.hourly_offset(valid)
    with ncopen(iemre.get_hourly_ncname(valid.year), "a", timeout=300) as nc:
        LOG.info(
            "offset: %s writing %s with min: %s max: %s Ames: %s",
            offset,
            vname,
            np.nanmin(grid),
            np.nanmax(grid),
            grid[151, 259],
        )
        nc.variables[vname][offset] = grid


def main(argv):
    """Go Main"""
    ts = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    grid_hour(ts)


if __name__ == "__main__":
    main(sys.argv)
