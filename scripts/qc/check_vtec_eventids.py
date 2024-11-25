"""
My purpose in life is to daily check the VTEC database and see if there are
any IDs that are missing.  daryl then follows up with the weather bureau
reporting anything he finds after an investigation.

called from RUN_MIDNIGHT.sh
"""

from datetime import datetime

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()


def main():
    """Go Main Go"""
    year = datetime.now().year

    with get_sqlalchemy_conn("postgis") as conn:
        missingdf = pd.read_sql(
            text(
                "select wfo || '.'|| phenomena ||'.'|| significance ||'.'|| "
                "eventid as key from vtec_missing_events WHERE year = :year"
            ),
            conn,
            params={"year": year},
        )
        eventsdf = pd.read_sql(
            text(
                "select distinct wfo, phenomena, significance, eventid "
                "from warnings where vtec_year = :year and "
                "phenomena not in ('TR', 'HU', 'SS') ORDER by "
                "wfo, phenomena, significance, eventid"
            ),
            conn,
            params={"year": year},
        )
    LOG.info("Currently %s known missing VTEC events", len(missingdf.index))
    LOG.info("Currently %s known VTEC events", len(eventsdf.index))

    newmissing = []
    for (wfo, phenomena, significance), gdf in eventsdf.groupby(
        ["wfo", "phenomena", "significance"]
    ):
        # These are national ETNs
        if phenomena in ("TO", "SV") and significance == "A":
            continue
        # Close enough check
        if len(gdf.index) == gdf["eventid"].max():
            continue
        # OK, we should have values from 1 to max
        miss = set(range(1, gdf["eventid"].max() + 1)) - set(gdf["eventid"])
        for eventid in miss:
            key = f"{wfo}.{phenomena}.{significance}.{eventid}"
            if key in missingdf["key"].values:
                continue
            LOG.warning("Missing %s", key)
            newmissing.append(
                {
                    "year": year,
                    "wfo": wfo,
                    "phenomena": phenomena,
                    "significance": significance,
                    "eventid": eventid,
                }
            )

    if not newmissing:
        return
    with get_sqlalchemy_conn("postgis") as conn:
        conn.execute(
            text(
                "INSERT into vtec_missing_events(year, wfo, phenomena, "
                "significance, eventid) VALUES (:year,:wfo,:phenomena,"
                ":significance,:eventid)"
            ),
            newmissing,
        )
        conn.commit()


if __name__ == "__main__":
    main()
