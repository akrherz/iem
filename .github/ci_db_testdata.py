"""Update The Test Database.

The test database instance for CI has static data for testing.  This is static
from the time of the docker image build.  This script runs from GHA and does
some mucking with the database to improve coverage.

"""

from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


@with_sqlalchemy_conn("isuag")
def create_realtime_isuag(conn: Connection = None) -> None:
    """Create the realtime table if needed."""
    nt = NetworkTable("ISUSM")
    for sid in nt.sts:
        conn.execute(
            sql_helper("""
    insert into sm_minute (station, valid, tair_c_avg_qc, sv_t2_qc,
    sv_vwc2_qc) values
    (:sid, now(), :tmpc, :tmpc, :vwc)"""),
            {
                "sid": sid,
                "tmpc": None if sid == "AHDI4" else 20.0,
                "vwc": None if sid in ["AMFI4", "AHDI4"] else 0.2,
            },
        )
        conn.execute(
            sql_helper("""
    insert into sm_daily (station, valid, tair_c_max_qc) values
    (:sid, now(), :tmpc)"""),
            {"sid": sid, "tmpc": 20.0},
        )
        if sid in ["CRFI4", "BOOI4", "CAMI4"]:
            conn.execute(
                sql_helper("""
        insert into sm_inversion (station, valid, tair_15_c_avg_qc) values
        (:sid, now(), :tmpc)"""),
                {"sid": sid, "tmpc": 20.0},
            )

    conn.commit()


@with_sqlalchemy_conn("iem")
def create_iemaccess_isuag(conn: Connection = None) -> None:
    """Create the realtime table if needed."""
    nt = NetworkTable("ISUSM")
    for sid in nt.sts:
        conn.execute(
            sql_helper("""
    insert into current (iemid, valid, tmpf) values
    (:iemid, now(), :tmpf)"""),
            {
                "iemid": nt.sts[sid]["iemid"],
                "tmpf": 20.0 if sid[2] > "F" else None,
            },
        )
    conn.commit()


@with_sqlalchemy_conn("id3b")
def ldm_product_log(conn: Connection = None) -> None:
    """Update these to the future."""
    conn.execute(
        sql_helper("""
    update ldm_product_log SET
    entered_at = now() - ('2024-12-03 19:30+00'::timestamptz - entered_at),
    valid_at = now() - ('2024-12-03 19:30+00'::timestamptz - valid_at),
    wmo_valid_at = now() -
    ('2024-12-03 19:30+00'::timestamptz - wmo_valid_at)
    where entered_at between '2024-12-03 16:00+00'
    and '2024-12-03 20:00+00'
""")
    )
    conn.commit()


@with_sqlalchemy_conn("radar")
def nexrad_attributes(conn: Connection = None) -> None:
    """Update these to be current."""
    res = conn.execute(
        sql_helper("update nexrad_attributes SET valid = now()")
    )
    LOG.warning("Updated %s nexrad_attributes to current time", res.rowcount)
    conn.commit()


def main():
    """Go Main."""
    ldm_product_log()
    nexrad_attributes()
    create_realtime_isuag()
    create_iemaccess_isuag()


if __name__ == "__main__":
    main()
