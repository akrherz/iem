"""Backfill IEMAccess Summary table.

Some of the variables don't get properly updated in the summary table.

cronjob from RUN_2AM.sh
"""

from datetime import date, datetime

import click
import pandas as pd
from metpy.calc import wind_components, wind_direction
from metpy.units import units
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.util import convert_value, logger

LOG = logger()


def process(pgconn, obs: pd.DataFrame):
    """option 1"""
    wcursor = pgconn.cursor()
    for iemid, row in obs.iterrows():
        table = f"summary_{row['valid']:%Y}"
        wcursor.execute(
            f"""
    UPDATE {table} SET avg_rh = %s, max_gust = %s, max_gust_ts = %s,
    avg_sknt = %s WHERE iemid = %s and day = %s
            """,
            (
                row["rh_avg_qc"],
                convert_value(row["ws_mph_max_qc"], "mph", "knot"),
                row["ws_mph_tmx_qc"],
                convert_value(row["ws_mph_qc"], "mph", "knot"),
                iemid,
                row["valid"],
            ),
        )
        if wcursor.rowcount == 0:
            LOG.warning("Adding summary row for iemid: %s", iemid)
            wcursor.execute(
                f"""
    INSERT INTO {table} (iemid, day, avg_rh, max_gust, max_gust_ts, avg_sknt)
    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    iemid,
                    row["valid"],
                    row["rh_avg_qc"],
                    convert_value(row["ws_mph_max_qc"], "mph", "knot"),
                    row["ws_mph_tmx_qc"],
                    convert_value(row["ws_mph_qc"], "mph", "knot"),
                ),
            )
    wcursor.close()


def compute_drct(dt: date):
    """Do things the hard way, because that is what we do."""
    with get_sqlalchemy_conn("isuag") as conn:
        obs = pd.read_sql(
            sql_helper("""
    select station, ws_mph_qc, winddir_d1_wvt_qc
    from sm_minute where valid > :dt and valid < :dt + interval '1 day'
    and ws_mph_qc > 0 and winddir_d1_wvt_qc >= 0
    """),
            conn,
            params={"dt": dt},
        )
    obs["u"], obs["v"] = wind_components(
        obs["ws_mph_qc"].values * units("mph"),
        obs["winddir_d1_wvt_qc"].values * units.degrees,
    )
    with (
        get_sqlalchemy_conn("iem") as iemconn,
        get_sqlalchemy_conn("isuag") as isuagconn,
    ):
        for station, gdf in obs.groupby("station"):
            u = gdf["u"].mean()
            v = gdf["v"].mean()
            if u == 0 and v == 0:
                continue
            drct = float(
                wind_direction(u * units("mph"), v * units("mph"))
                .to("degrees")
                .m
            )
            isuagconn.execute(
                sql_helper("""
                        update sm_daily SET winddir_d1_wvt_qc = :drct,
                            winddir_d1_wvt = :drct
                        where station = :station and valid = :dt and
                        winddir_d1_wvt_qc is null
                        """),
                {"drct": drct, "station": station, "dt": dt},
            )
            isuagconn.commit()
            iemconn.execute(
                sql_helper("""
                update summary s
                SET vector_avg_drct = :drct
                from stations t
                where s.iemid = t.iemid and t.id = :station
                        and t.network = 'ISUSM' and day = :dt
                            """),
                {"drct": drct, "station": station, "dt": dt},
            )
            iemconn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Date to process")
def main(dt: datetime):
    """Go Main Go"""
    dt = dt.date()
    with get_sqlalchemy_conn("isuag") as conn:
        obs = pd.read_sql(
            sql_helper("""
    select iemid, station, valid, rh_avg_qc, ws_mph_tmx_qc, ws_mph_qc,
    ws_mph_max_qc
    from sm_daily d JOIN stations t on (d.station = t.id)
    where valid = :dt and t.network = 'ISUSM'
    """),
            conn,
            params={"dt": dt},
            index_col="iemid",
        )
    with get_sqlalchemy_conn("iem") as conn:
        summary = pd.read_sql(
            sql_helper("""
    select d.iemid, avg_rh, max_gust, max_gust_ts, avg_sknt
    from summary d JOIN stations t on (d.iemid = t.iemid)
    where day = :dt and t.network = 'ISUSM'
    """),
            conn,
            params={"dt": dt},
            index_col="iemid",
        )
    obs = obs.join(summary, how="left", rsuffix="_summary")
    LOG.info(
        "Found %s obs for date: %s",
        len(obs.index),
        dt,
    )
    with get_dbconn("iem") as pgconn:
        process(pgconn, obs)
        pgconn.commit()

    # Lovely one-offs
    compute_drct(dt)


if __name__ == "__main__":
    main()
