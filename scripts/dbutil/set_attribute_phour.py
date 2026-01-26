"""Assign station attribute for those stations with hourly precip.

Run from RUN_MIDNIGHT.sh
"""

import pandas as pd
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import StationAttributes as SA
from pyiem.util import logger
from sqlalchemy.engine import Connection

LOG = logger()


@with_sqlalchemy_conn("mesosite")
def load_sites(conn: Connection | None = None) -> pd.DataFrame:
    """Figure out what we have."""
    df = pd.read_sql(
        sql_helper("""
    SELECT s.iemid from stations s JOIN station_attributes a ON
    (s.iemid = a.iemid) WHERE a.attr = :attr
        """),
        conn,
        params={"attr": SA.HAS_PHOUR},
        index_col="iemid",
    )
    LOG.info("Found %s stations with HAS_PHOUR attribute", len(df.index))
    return df


@with_sqlalchemy_conn("iem")
def load_obs(conn: Connection | None = None) -> pd.DataFrame:
    """Figure out who has HML data."""
    df = pd.read_sql(
        sql_helper("""
    select distinct iemid from hourly where valid >= 'TODAY' and
    valid < 'TOMORROW'
                 """),
        conn,
        index_col="iemid",
    )
    LOG.info("Found %s stations reporting precip over past day", len(df.index))
    return df


@with_sqlalchemy_conn("mesosite")
def update_mesosite(iemids: list[int], conn: Connection | None = None) -> None:
    """Set the metadata!"""
    for iemid in iemids:
        conn.execute(
            sql_helper("""
        INSERT into station_attributes (iemid, attr, value)
        VALUES (:iemid, :attr, '1')
            """),
            {"iemid": iemid, "attr": SA.HAS_PHOUR},
        )
    conn.commit()


def main():
    """Go."""
    currentdf = load_sites()
    obsdf = load_obs()
    LOG.info("hml has %s sites with HML data", len(obsdf.index))
    # Find the difference
    addsites = obsdf.index.difference(currentdf.index)
    if addsites.empty:
        return
    LOG.warning("Adding %s for %s sites", SA.HAS_PHOUR, len(addsites))
    update_mesosite(addsites.to_list())


if __name__ == "__main__":
    main()
