"""
Gridcell sample the ERA5Land NetCDF files to save srad to climodat database.

Run from RUN_0Z.sh for seven UTC days ago.
"""

from datetime import timedelta

import click
import geopandas as gpd
import numpy as np
import pandas as pd
from affine import Affine
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import NORTH, WEST, hourly_offset
from pyiem.util import convert_value, logger, ncopen, utc

LOG = logger()


def compute_regions(data, varname, df):
    """Do the spatial averaging work."""
    with get_sqlalchemy_conn("coop") as conn:
        gdf = gpd.read_postgis(
            """
            SELECT t.id, c.geom from stations t JOIN climodat_regions c on
            (t.iemid = c.iemid) ORDER by t.id ASC
            """,
            conn,
            index_col="id",
            geom_col="geom",
        )
    affine = Affine(0.1, 0, WEST, 0, -0.1, NORTH)
    czs = CachingZonalStats(affine)
    data = czs.gen_stats(np.flipud(data), gdf["geom"])
    for i, sid in enumerate(gdf.index.values):
        df.at[sid, varname] = data[i]


def build_stations(dt) -> pd.DataFrame:
    """Figure out what we need data for."""
    with get_sqlalchemy_conn("coop") as conn:
        # There's a lone VICLIMATE site at -65 :/
        df = pd.read_sql(
            """
            SELECT station, st_x(geom) as lon, st_y(geom) as lat, temp_hour
            from alldata a JOIN stations t on (a.station = t.id) WHERE
            t.network ~* 'CLIMATE' and a.day = %s and
            st_x(geom) between -127 and -65.1
            ORDER by station ASC
            """,
            conn,
            params=(dt,),
            index_col="station",
        )
    for col in [
        "era5land_srad",
        "era5land_soilt4_avg",
        "era5land_soilm4_avg",
        "era5land_soilm1m_avg",
    ]:
        df[col] = np.nan
    df["i"] = np.nan
    df["j"] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def compute(df, sids, dt, do_regions=False):
    """Do the magic."""
    # Life choice is to run 6z to 6z
    sts = utc(dt.year, dt.month, dt.day, 6)
    ets = sts + timedelta(hours=24)

    ncfn = f"/mesonet/data/era5/{sts.year}_era5land_hourly.nc"
    idx0 = hourly_offset(sts)
    idx1 = hourly_offset(ets)
    # Wm-2 to MJ
    factor = 3600.0 / 1_000_000.0
    with ncopen(ncfn) as nc:
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
        if f"{dt:%m%d}" == "1231":
            rsds = np.sum(nc.variables["rsds"][idx0:], 0) * factor
            # Close enough
            soilm = np.mean(nc.variables["soilm"][idx0:, 0], 0)
            soilm1m = (
                np.mean(nc.variables["soilm"][idx0:, 0], 0) * 7.0
                + np.mean(nc.variables["soilm"][idx0:, 1], 0) * 21.0
                + np.mean(nc.variables["soilm"][idx0:, 2], 0) * 72.0
            ) / 100.0
            soilt = np.mean(nc.variables["soilt"][idx0:, 0], 0)
            ncfn2 = f"/mesonet/data/era5/{ets.year}_era5land_hourly.nc"
            with ncopen(ncfn2) as nc2:
                rsds += np.sum(nc2.variables["rsds"][:idx1], 0) * factor
        else:
            rsds = np.sum(nc.variables["rsds"][idx0:idx1], 0) * factor
            soilm = np.mean(nc.variables["soilm"][idx0:idx1, 0], 0)
            soilm1m = (
                np.mean(nc.variables["soilm"][idx0:idx1, 0], 0) * 7.0
                + np.mean(nc.variables["soilm"][idx0:idx1, 1], 0) * 21.0
                + np.mean(nc.variables["soilm"][idx0:idx1, 2], 0) * 72.0
            ) / 100.0
            soilt = np.mean(nc.variables["soilt"][idx0:idx1, 0], 0)

    df["i"] = np.digitize(df["lon"].values, lons)
    df["j"] = np.digitize(df["lat"].values, lats)
    rsds = rsds.filled(np.nan)
    soilm = soilm.filled(np.nan)
    soilm1m = soilm1m.filled(np.nan)
    soilt = soilt.filled(np.nan)

    for sid, row in df.loc[sids].iterrows():
        df.at[sid, "era5land_srad"] = rsds[int(row["j"]), int(row["i"])]
        df.at[sid, "era5land_soilt4_avg"] = soilt[int(row["j"]), int(row["i"])]
        df.at[sid, "era5land_soilm4_avg"] = soilm[int(row["j"]), int(row["i"])]
        df.at[sid, "era5land_soilm1m_avg"] = soilm1m[
            int(row["j"]), int(row["i"])
        ]

    if do_regions:
        compute_regions(rsds, "era5land_srad", df)
        compute_regions(soilt, "era5land_soilt4_avg", df)
        compute_regions(soilm, "era5land_soilm4_avg", df)
        compute_regions(soilm1m, "era5land_soilm1m_avg", df)

    LOG.info("IA0200 %s", df.loc["IA0200"])


def do(dt):
    """Process for a given date."""
    LOG.info("do(%s)", dt)
    df = build_stations(dt)
    df["day"] = dt
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's values
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df["era5land_srad"].isna()].index.values
    compute(df, sids, dt)

    df["station"] = df.index.values
    df["era5land_soilt4_avg"] = convert_value(
        df["era5land_soilt4_avg"].values, "degK", "degF"
    )

    # prevent NaN from being inserted
    df = df.replace({np.nan: None})
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    cursor.executemany(
        """
        UPDATE alldata set era5land_srad = %(era5land_srad)s,
        era5land_soilt4_avg = %(era5land_soilt4_avg)s,
        era5land_soilm4_avg = %(era5land_soilm4_avg)s,
        era5land_soilm1m_avg = %(era5land_soilm1m_avg)s
        where station = %(station)s and day = %(day)s
        """,
        df.to_dict("records"),
    )
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--date", "valid", type=click.DateTime())
def main(valid):
    """Go Main Go"""
    do(valid.date())


if __name__ == "__main__":
    main()
