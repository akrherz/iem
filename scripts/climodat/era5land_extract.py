"""
Do ERA5Land grid cell sampling to populate climodat station estimates.

Run from RUN_0Z.sh for seven UTC days ago.
Run from RUN_NOON.sh for today and yesterday using iemre.
"""

from datetime import date, datetime, timedelta

import click
import geopandas as gpd
import numpy as np
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.grid.nav import get_nav
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import hourly_offset
from pyiem.util import convert_value, logger, ncopen, utc

LOG = logger()


def compute_regions(
    data: np.ndarray, varname: str, df: pd.DataFrame, use_iemre: bool
):
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
    czs = CachingZonalStats(
        get_nav("IEMRE" if use_iemre else "ERA5LAND", "CONUS").affine_image
    )
    data = czs.gen_stats(np.flipud(data), gdf["geom"])
    for i, sid in enumerate(gdf.index.values):
        if np.ma.is_masked(data[i]):
            LOG.info("No data for %s %s", sid, varname)
            continue
        df.at[sid, varname] = data[i]


def build_stations(dt: date) -> pd.DataFrame:
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
        "era5land_soilt4_min",
        "era5land_soilt4_max",
        "era5land_soilm4_avg",
        "era5land_soilm1m_avg",
    ]:
        df[col] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def compute(df, sids, dt, do_regions: bool, use_iemre: bool):
    """Do the magic."""
    # Life choice is to run 6z to 6z
    sts = utc(dt.year, dt.month, dt.day, 6)
    ets = sts + timedelta(hours=24)

    ncfn = f"/mesonet/data/era5/{sts.year}_era5land_hourly.nc"
    if use_iemre:
        ncfn = f"/mesonet/data/iemre/{sts.year}_iemre_hourly.nc"
    idx0 = hourly_offset(sts)
    idx1 = hourly_offset(ets)
    # Wm-2 to MJ
    factor = 3600.0 / 1_000_000.0
    soilm = None
    soilm1m = None
    with ncopen(ncfn) as nc:
        if f"{dt:%m%d}" == "1231":
            rsds = np.sum(nc.variables["rsds"][idx0:], 0) * factor
            if "soilm" in nc.variables:
                # Close enough
                soilm = np.mean(nc.variables["soilm"][idx0:, 0], 0)
                soilm1m = (
                    np.mean(nc.variables["soilm"][idx0:, 0], 0) * 7.0
                    + np.mean(nc.variables["soilm"][idx0:, 1], 0) * 21.0
                    + np.mean(nc.variables["soilm"][idx0:, 2], 0) * 72.0
                ) / 100.0
                soiltmin = np.min(nc.variables["soilt"][idx0:, 0], 0)
                soiltmax = np.max(nc.variables["soilt"][idx0:, 0], 0)
            else:
                soiltmin = np.min(nc.variables["soil4t"][idx0:], 0)
                soiltmax = np.max(nc.variables["soil4t"][idx0:], 0)

            ncfn2 = f"/mesonet/data/era5/{ets.year}_era5land_hourly.nc"
            if use_iemre:
                ncfn2 = f"/mesonet/data/iemre/{ets.year}_iemre_hourly.nc"
            with ncopen(ncfn2) as nc2:
                rsds += np.sum(nc2.variables["rsds"][:idx1], 0) * factor
        else:
            rsds = np.sum(nc.variables["rsds"][idx0:idx1], 0) * factor
            if "soilm" in nc.variables:
                soilm = np.mean(nc.variables["soilm"][idx0:idx1, 0], 0)
                soilm1m = (
                    np.mean(nc.variables["soilm"][idx0:idx1, 0], 0) * 7.0
                    + np.mean(nc.variables["soilm"][idx0:idx1, 1], 0) * 21.0
                    + np.mean(nc.variables["soilm"][idx0:idx1, 2], 0) * 72.0
                ) / 100.0
                soiltmin = np.min(nc.variables["soilt"][idx0:idx1, 0], 0)
                soiltmax = np.max(nc.variables["soilt"][idx0:idx1, 0], 0)
            else:
                soiltmin = np.min(nc.variables["soil4t"][idx0:idx1], 0)
                soiltmax = np.max(nc.variables["soil4t"][idx0:idx1], 0)

    rsds = rsds.filled(np.nan)
    if soilm is not None:
        soilm = soilm.filled(np.nan)
        soilm1m = soilm1m.filled(np.nan)
    soiltmin = soiltmin.filled(np.nan)
    soiltmax = soiltmax.filled(np.nan)

    for sid, row in df.loc[sids].iterrows():
        i, j = get_nav("IEMRE" if use_iemre else "ERA5LAND", "CONUS").find_ij(
            row["lon"], row["lat"]
        )
        if i is None:
            continue
        df.at[sid, "era5land_srad"] = rsds[j, i]
        df.at[sid, "era5land_soilt4_min"] = soiltmin[j, i]
        df.at[sid, "era5land_soilt4_max"] = soiltmax[j, i]
        if soilm is not None:
            df.at[sid, "era5land_soilm4_avg"] = soilm[j, i]
            df.at[sid, "era5land_soilm1m_avg"] = soilm1m[j, i]

    if do_regions:
        compute_regions(rsds, "era5land_srad", df, use_iemre)
        compute_regions(soiltmin, "era5land_soilt4_min", df, use_iemre)
        compute_regions(soiltmax, "era5land_soilt4_max", df, use_iemre)
        if soilm is not None:
            compute_regions(soilm, "era5land_soilm4_avg", df, use_iemre)
            compute_regions(soilm1m, "era5land_soilm1m_avg", df, use_iemre)

    if "IA0200" in df.index:
        LOG.info("IA0200 %s", df.loc["IA0200"])


def do(dt: date, use_iemre: bool):
    """Process for a given date."""
    LOG.info("do(%s) using iemre: %s", dt, use_iemre)
    df = build_stations(dt)
    df["day"] = dt
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's values
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - timedelta(days=1), True, use_iemre)
    # 2. All other sites get today
    sids = df[df["era5land_srad"].isna()].index.values
    compute(df, sids, dt, False, use_iemre)

    df["station"] = df.index.values
    df["era5land_soilt4_min"] = convert_value(
        df["era5land_soilt4_min"].values, "degK", "degF"
    )
    df["era5land_soilt4_max"] = convert_value(
        df["era5land_soilt4_max"].values, "degK", "degF"
    )

    # prevent NaN from being inserted
    df = df.replace({np.nan: None})
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    cursor.executemany(
        """
        UPDATE alldata set era5land_srad = %(era5land_srad)s,
        era5land_soilt4_min = %(era5land_soilt4_min)s,
        era5land_soilt4_max = %(era5land_soilt4_max)s,
        era5land_soilm4_avg = %(era5land_soilm4_avg)s,
        era5land_soilm1m_avg = %(era5land_soilm1m_avg)s
        where station = %(station)s and day = %(day)s
        """,
        df.to_dict("records"),
    )
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--date", "valid", type=click.DateTime(), required=True)
@click.option(
    "--use-iemre",
    is_flag=True,
    help="Use IEMRE as the sampling source, which is IFS, so ERA5Land.",
)
def main(valid: datetime, use_iemre: bool):
    """Go Main Go"""
    do(valid.date(), use_iemre)


if __name__ == "__main__":
    main()
