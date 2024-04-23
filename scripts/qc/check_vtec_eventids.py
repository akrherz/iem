"""
My purpose in life is to daily check the VTEC database and see if there are
any IDs that are missing.  daryl then follows up with the weather bureau
reporting anything he finds after an investigation.

called from RUN_MIDNIGHT.sh
"""

import datetime

from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main Go"""
    pgconn = get_dbconn("postgis")
    pcursor = pgconn.cursor()
    pcursor2 = pgconn.cursor()

    year = datetime.datetime.now().year

    pcursor.execute(
        "SELECT wfo, phenomena, significance, eventid from "
        "vtec_missing_events WHERE year = %s",
        (year,),
    )
    missing = [f"{row[0]}.{row[1]}.{row[2]}.{row[3]}" for row in pcursor]

    # Gap analysis!
    sql = f"""
    with data as (
        select distinct wfo, phenomena, significance, eventid
        from warnings_{year}),
    deltas as (
        SELECT wfo, eventid, phenomena, significance,
        eventid - lag(eventid) OVER (PARTITION by wfo, phenomena, significance
                                     ORDER by eventid ASC) as delta
        from data)

    SELECT wfo, eventid, phenomena, significance, delta from deltas
    WHERE delta > 1 ORDER by wfo ASC
    """
    pcursor.execute(sql)
    for row in pcursor:
        phenomena = row[2]
        wfo = row[0]
        sig = row[3]
        gap = row[4]
        eventid = row[1]

        # Skip these
        if phenomena in ("TR", "HU", "SS") or (
            phenomena in ("TO", "SV", "SS") and sig == "A"
        ):
            continue

        for eid in range(eventid - gap + 1, eventid):
            lookup = f"{wfo}.{phenomena}.{sig}.{eid}"
            if lookup in missing:
                continue
            pcursor2.execute(
                "INSERT into vtec_missing_events(year, wfo, phenomena, "
                "significance, eventid) VALUES (%s,%s,%s,%s,%s)",
                (year, wfo, phenomena, sig, eid),
            )
            LOG.warning(
                "WWA missing WFO: %s phenomena: %s sig: %s eventid: %s",
                wfo,
                phenomena,
                sig,
                eid,
            )

    pcursor2.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
