"""
Extract NASA POWER solar radiation for IEM Long Term Climate Sites.

refs akrherz/iem#385

Since POWER data is courser than the IEMRE grid, we can just sample IEMRE.

Run from RUN_2AM.sh looking for missing data to estimate.
"""

import datetime
from typing import Optional

import click
import geopandas as gpd
import numpy as np
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import AFFINE, daily_offset, get_daily_ncname
from pyiem.util import logger, ncopen
from sqlalchemy import text

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
    czs = CachingZonalStats(AFFINE)
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
    df["power_srad"] = np.nan
    df["i"] = np.nan
    df["j"] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def compute(df, sids, dt: datetime.date, do_regions=False):
    """Do the magic."""
    ncfn = get_daily_ncname(dt.year, domain="")
    tidx = daily_offset(dt)
    with ncopen(ncfn) as nc:
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
        power_srad = nc.variables["power_swdn"][tidx].filled(np.nan)

    df["i"] = np.digitize(df["lon"].values, lons) - 1
    df["j"] = np.digitize(df["lat"].values, lats) - 1

    for sid, row in df.loc[sids].iterrows():
        df.at[sid, "power_srad"] = power_srad[int(row["j"]), int(row["i"])]

    if do_regions:
        compute_regions(power_srad, "power_srad", df)

    LOG.info("IA0200 %s", df.loc["IA0200"])


def do(dt: datetime.date):
    """Process for a given date."""
    LOG.info("do(%s)", dt)
    df = build_stations(dt)
    df["day"] = dt
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's values
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - datetime.timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df["power_srad"].isna()].index.values
    compute(df, sids, dt)

    df["station"] = df.index.values
    # prevent NaN from being inserted
    df = df.replace({np.nan: None})
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    cursor.executemany(
        """
        UPDATE alldata set power_srad = %(power_srad)s
        where station = %(station)s and day = %(day)s
        """,
        df.to_dict("records"),
    )
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--date", "valid", type=click.DateTime())
def main(valid: Optional[datetime.datetime]):
    """Go Main Go"""
    if valid is not None:
        do(valid.date())
        return
    with get_sqlalchemy_conn("coop") as conn:
        days = pd.read_sql(
            text("""
                SELECT day from alldata_ia where station = 'IATAME'
                and power_srad is null and day >= '1984-01-01'
                ORDER by day ASC LIMIT 100
            """),
            conn,
            index_col=None,
        )
        if days.empty:
            LOG.info("No days to process!")
            return
        for _, row in days.iterrows():
            do(row["day"])


if __name__ == "__main__":
    main()
