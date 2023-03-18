"""
 Sample the NARR solar radiation analysis into estimated values for the
 COOP point archive

 1 langley is 41840.00 J m-2 is 41840.00 W s m-2 is 11.622 W hr m-2

 So 1000 W m-2 x 3600 is 3,600,000 W s m-2 is 86 langleys

 Updated: to match other columns, we are storing in MJ/day/m2 now!

 26 Jun 1988 is bad!


 http://rda.ucar.edu/dataset/ds608.0

Updates of NARR data from April 1, 2009 to January 31, 2015
released by NCEP have been archived as "rerun4" version of ds608.0
dataset in rda.ucar.edu in May 2015.  This update fixes the codes
that read Mexican precipitation data and a bug introduced when NCEP
switched the computer systems. The direct effects of these changes
are in the precipitation and in the soil moisture fields.

Review the following pdf file for details.
    http://rda.ucar.edu/datasets/ds608.0/docs/rr4.pdf

"""
import datetime
import os
import sys

from affine import Affine
import numpy as np
import pandas as pd
import pygrib
import pyproj
import geopandas as gpd
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import get_dbconn, logger, get_sqlalchemy_conn, utc

LOG = logger()
LCC = (
    "+proj=lcc +lon_0=-107.0 +y_0=0.0 +R=6367470.21484 "
    "+x_0=0.0 +units=m +lat_2=50.0 +lat_1=50.0 +lat_0=50.0"
)


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


def compute_regions(affine, rsds, df):
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
        df.at[sid, "narr_srad"] = data[i]


def compute(df, sids, dt, do_regions=False):
    """Process data for this timestamp"""
    LOG.info("called dt: %s len(sids): %s", dt, len(sids))
    # Life choice is to run 6z to 6z
    now = utc(dt.year, dt.month, dt.day, 6)
    ets = now + datetime.timedelta(hours=24)
    total = None
    xaxis = None
    yaxis = None
    while now < ets:
        # See if we have Grib data first
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/NARR/rad_%Y%m%d%H00.grib"
        )
        if not os.path.isfile(fn):
            LOG.warning("Missing %s", fn)
        else:
            grb = pygrib.open(fn)[1]
            if total is None:
                xaxis, yaxis = get_grid(grb)
                affine = Affine(
                    grb["DxInMetres"],
                    0,
                    xaxis[0],
                    0,
                    0 - grb["DyInMetres"],
                    yaxis[-1],
                )

                # W/m2 over 3 hours J/m2 to MJ/m2
                total = grb["values"] * 10800.0 / 1_000_000.0
            else:
                total += grb["values"] * 10800.0 / 1_000_000.0
        now += datetime.timedelta(hours=3)

    df["i"] = np.digitize(df["projx"].values, xaxis)
    df["j"] = np.digitize(df["projy"].values, yaxis)
    for sid, row in df.loc[sids].iterrows():
        df.at[sid, "narr_srad"] = total[int(row["j"]), int(row["i"])]

    if do_regions:
        compute_regions(affine, total, df)

    LOG.info("IA0200 %s", df.at["IA0200", "narr_srad"])


def build_stations(dt) -> pd.DataFrame:
    """Figure out what we need data for."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT station, st_x(ST_Transform(geom, %s)) as projx,
            st_y(st_transform(geom, %s)) as projy, temp_hour
            from alldata a JOIN stations t on (a.station = t.id) WHERE
            t.network ~* 'CLIMATE' and a.day = %s and
            state not in ('PR', 'HI', 'GU')
            ORDER by station ASC
            """,
            conn,
            params=(LCC, LCC, dt),
            index_col="station",
        )
    df["narr_srad"] = np.nan
    df["i"] = np.nan
    df["j"] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def do(dt):
    """Process for a given date
    6z file has 6z to 9z data
    """
    df = build_stations(dt)
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's radiation
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - datetime.timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df["narr_srad"].isna()].index.values
    compute(df, sids, dt)

    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()

    for sid, row in df[df["narr_srad"].notna()].iterrows():
        cursor.execute(
            "UPDATE alldata set narr_srad = %s where station = %s and "
            "day = %s",
            (row["narr_srad"], sid, dt),
        )

    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        do(datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3])))
    if len(argv) == 3:
        # Run for a given month, but include the last day of the previous month
        sts = datetime.datetime(
            int(argv[1]), int(argv[2]), 1
        ) - datetime.timedelta(days=1)
        ets = sts + datetime.timedelta(days=45)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do(now)
            now += datetime.timedelta(days=1)


if __name__ == "__main__":
    main(sys.argv)
