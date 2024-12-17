"""Extract HRRR radiation data for storage with COOP data.

Run once at 10 PM to snag calendar day stations. (RUN_50_AFTER.sh)
Run again with RUN_NOON.sh when the regular estimator runs
"""

# pylint: disable=unpacking-non-sequence
import datetime

import click
import geopandas as gpd
import numpy as np
import pandas as pd
import pygrib
import pyproj
from affine import Affine
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import archive_fetch, logger, utc

LOG = logger()
LCC = (
    "+proj=lcc +lon_0=-97.5 +y_0=0.0 +R=6367470. +x_0=0.0"
    " +units=m +lat_2=38.5 +lat_1=38.5 +lat_0=38.5"
)
COL = "hrrr_srad"

# NOTE: for unsure reasons, the old HRRR data prior to this timestamp gets
# invalidly decoded by present day pygrib, so we just abort for now.
SWITCH_DATE = utc(2014, 10, 10, 20)
GRBNAME = "Time-mean surface downward short-wave radiation flux"


def compute_regions(affine: Affine, rsds, df):
    """Do the spatial averaging work."""
    with get_sqlalchemy_conn("coop") as conn:
        gdf = gpd.read_postgis(
            """
            SELECT t.id, ST_Transform(c.geom, %s) as geo
            from stations t JOIN climodat_regions c on
            (t.iemid = c.iemid) ORDER by t.id ASC
            """,
            conn,
            index_col="id",
            params=(LCC,),
            geom_col="geo",
        )
    czs = CachingZonalStats(affine)
    data = czs.gen_stats(np.flipud(rsds), gdf["geo"])
    for i, sid in enumerate(gdf.index.values):
        df.at[sid, COL] = data[i]


def build_stations(dt) -> pd.DataFrame:
    """Figure out what we need data for."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT station, st_x(ST_Transform(geom, %s)) as projx,
            st_y(st_transform(geom, %s)) as projy, temp_hour
            from alldata a JOIN stations t on (a.station = t.id) WHERE
            t.network ~* 'CLIMATE' and a.day = %s and
            st_x(geom) between -127 and -65 and state != 'PR'
            ORDER by station ASC
            """,
            conn,
            params=(LCC, LCC, dt),
            index_col="station",
        )
    df[COL] = np.nan
    df["i"] = np.nan
    df["j"] = np.nan
    df["day"] = dt
    LOG.info("Found %s database entries", len(df.index))
    return df


def get_grid(grb):
    """Figure out the x-y coordinates."""
    pj = pyproj.Proj(grb.projparams)
    # ll
    lat1 = grb["latitudeOfFirstGridPointInDegrees"]
    lon1 = grb["longitudeOfFirstGridPointInDegrees"]
    llx, lly = pj(lon1, lat1)
    xaxis = llx + grb["DxInMetres"] * np.arange(grb["Nx"])
    yaxis = lly + grb["DyInMetres"] * np.arange(grb["Ny"])
    return xaxis, yaxis


def compute(df: pd.DataFrame, sids, dt, do_regions=False):
    """Process data for this timestamp"""
    # Life choice is to run 6z to 6z
    sts = utc(dt.year, dt.month, dt.day, 6)
    if sts < SWITCH_DATE:
        LOG.warning("Aborting due to inability to process archive.")
        return
    total = None
    xaxis = None
    yaxis = None
    # date_range is inclusive
    for now in pd.date_range(
        sts, sts + datetime.timedelta(hours=23), freq="1h"
    ):
        # Try the newer f01 files, which have better data!
        with archive_fetch(
            now.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf01.grib2")
        ) as fn:
            if fn is not None:
                grbs = pygrib.open(fn)
                selgrbs = grbs.select(name=GRBNAME)
                if len(selgrbs) == 4:
                    # Goodie
                    for g in selgrbs:
                        if total is None:
                            xaxis, yaxis = get_grid(g)
                            # This is the outer edge, not center
                            affine = Affine(
                                g["DxInMetres"],
                                0,
                                xaxis[0] - g["DxInMetres"] / 2.0,
                                0,
                                0 - g["DyInMetres"],
                                yaxis[-1] + g["DyInMetres"] / 2.0,
                            )
                            total = g.values * 900.0  # 15 min data
                        else:
                            total += g.values * 900.0
                    continue
        with archive_fetch(
            now.strftime("%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf00.grib2")
        ) as fn:
            if fn is None:
                LOG.info("Missing %s", now)
                continue
            grbs = pygrib.open(fn)
            try:
                if now >= SWITCH_DATE:
                    grb = grbs.select(name=GRBNAME)
                else:
                    grb = grbs.select(parameterNumber=192)
            except ValueError:
                continue
            g = grb[0]
            if total is None:
                xaxis, yaxis = get_grid(g)
                # This is the outer edge, not center
                affine = Affine(
                    g["DxInMetres"],
                    0,
                    xaxis[0] - g["DxInMetres"] / 2.0,
                    0,
                    0 - g["DyInMetres"],
                    yaxis[-1] + g["DyInMetres"] / 2.0,
                )
                total = g.values * 3600.0
            else:
                total += g.values * 3600.0

    if total is None:
        LOG.warning("No HRRR data for %s", dt)
        return

    # Total is the sum of the hourly values
    # We want MJ day-1 m-2
    total = total / 1_000_000.0

    df["i"] = np.digitize(df["projx"].to_numpy(), xaxis)
    df["j"] = np.digitize(df["projy"].to_numpy(), yaxis)
    for sid, row in df.loc[sids].iterrows():
        df.at[sid, COL] = total[int(row["j"]), int(row["i"])]

    if do_regions:
        compute_regions(affine, total, df)

    LOG.info("IA0200 %s", df.at["IA0200", COL])


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="UTC Valid Time")
def main(dt):
    """Do Something"""
    dt = dt.date()
    df = build_stations(dt)
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's radiation
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - datetime.timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df[COL].isna()].index.values
    compute(df, sids, dt)

    pgconn, cursor = get_dbconnc("coop")
    cursor.executemany(  # skipcq
        f"UPDATE alldata set {COL} = %({COL})s where station = %(station)s "
        "and day = %(day)s",
        df[df[COL].notna()].reset_index().to_dict("records"),
    )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
