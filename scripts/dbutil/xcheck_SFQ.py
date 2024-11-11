"""Cross SHEF sites reporting SFQ and not assigned to a ASOS/WFO.

Run from RUN_0Z.sh
"""

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import StationAttributes as SA
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()


def load_sites() -> pd.DataFrame:
    """Figure out what we have."""
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            text("""
    SELECT id, value as snow_src from stations s JOIN station_attributes a ON
    (s.iemid = a.iemid) WHERE a.attr = :attr
            """),
            conn,
            params={"attr": SA.SHEF_6HR_SRC},
            index_col="id",
        )
    return df


def load_obs() -> pd.DataFrame:
    """Figure out who has HML data."""
    with get_sqlalchemy_conn("hads") as conn:
        df = pd.read_sql(
            text("""
    select distinct station from raw where
    valid > now() - '7 days'::interval and substr(key, 1, 3) = 'SFQ'
                 """),
            conn,
            index_col="station",
        )
    return df


def main():
    """Go."""
    currentdf = load_sites()
    LOG.info(
        "mesosite has %s sites with %s", len(currentdf.index), SA.SHEF_6HR_SRC
    )
    obsdf = load_obs()
    LOG.info("hml has %s sites with HML data", len(obsdf.index))
    # Find the difference
    addsites = obsdf.index.difference(currentdf["snow_src"])
    if addsites.empty:
        return
    LOG.warning("Found %s SFQ sites without metadata.", len(addsites))
    print(addsites.to_list())


if __name__ == "__main__":
    main()
