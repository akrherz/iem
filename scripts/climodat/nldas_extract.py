"""
Gridcell sample the NLDAS NetCDF files to save srad to climodat database.

Run from RUN_0Z.sh for six UTC days ago.
"""
import datetime

import click
import geopandas as gpd
import numpy as np
import pandas as pd
from affine import Affine
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import hourly_offset
from pyiem.util import (
    convert_value,
    get_dbconn,
    get_sqlalchemy_conn,
    logger,
    ncopen,
    utc,
)

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
    affine = Affine(0.125, 0, -125.0, 0, -0.125, 53.0)
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
    for col in ["nldas_soilt4_avg", "nldas_soilm4_avg"]:
        df[col] = np.nan
    df["i"] = np.nan
    df["j"] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def compute(df, sids, dt, do_regions=False):
    """Do the magic."""
    # Life choice is to run 6z to 6z
    sts = utc(dt.year, dt.month, dt.day, 6)
    ets = sts + datetime.timedelta(hours=24)

    ncfn = f"/mesonet/data/nldas/{sts.year}_hourly.nc"
    idx0 = hourly_offset(sts)
    idx1 = hourly_offset(ets)
    with ncopen(ncfn) as nc:
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
        if f"{dt:%m%d}" == "1231":
            # Close enough
            soilm = np.mean(nc.variables["soilm"][idx0:, 0], 0)
            soilt = np.mean(nc.variables["soilt"][idx0:, 0], 0)
        else:
            soilm = np.mean(nc.variables["soilm"][idx0:idx1, 0], 0)
            soilt = np.mean(nc.variables["soilt"][idx0:idx1, 0], 0)

    df["i"] = np.digitize(df["lon"].values, lons)
    df["j"] = np.digitize(df["lat"].values, lats)
    soilm = soilm.filled(np.nan)
    soilt = soilt.filled(np.nan)

    for sid, row in df.loc[sids].iterrows():
        df.at[sid, "nldas_soilt4_avg"] = soilt[int(row["j"]), int(row["i"])]
        df.at[sid, "nldas_soilm4_avg"] = soilm[int(row["j"]), int(row["i"])]

    if do_regions:
        compute_regions(soilt, "nldas_soilt4_avg", df)
        compute_regions(soilm, "nldas_soilm4_avg", df)

    LOG.info("IA0200 %s", df.loc["IA0200"])


def do(dt):
    """Process for a given date."""
    LOG.info("do(%s)", dt)
    df = build_stations(dt)
    df["day"] = dt
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's values
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - datetime.timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df["nldas_soilt4_avg"].isna()].index.values
    compute(df, sids, dt)

    df["station"] = df.index.values
    df["nldas_soilt4_avg"] = convert_value(
        df["nldas_soilt4_avg"].values, "degK", "degF"
    )

    # prevent NaN from being inserted
    df = df.replace({np.nan: None})
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    cursor.executemany(
        """
        UPDATE alldata set
        nldas_soilt4_avg = %(nldas_soilt4_avg)s,
        nldas_soilm4_avg = %(nldas_soilm4_avg)s
        where station = %(station)s and day = %(day)s
        """,
        df.to_dict("records"),
    )
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--valid", type=click.DateTime())
def main(valid):
    """Go Main Go"""
    do(valid.date())


if __name__ == "__main__":
    main()
