"""COOP data gets corrected and whatnot.

We need to check the IEM Access database for any COOP sites with updated
data and then update the climodat database appropriately, ufff.

run from RUN_NOON.sh
"""
# pylint: disable=cell-var-from-loop

from pyiem.util import get_dbconn, logger
import pandas as pd
from pandas.io.sql import read_sql
from psycopg2.extras import DictCursor

LOG = logger()


def load_changes(accessdb):
    """Find what has changed."""
    df = read_sql(
        "SELECT distinct id, c.iemid, network, tzname, "
        "date(valid at time zone t.tzname) from current_log c JOIN "
        "stations t on (c.iemid = t.iemid) WHERE t.network ~* 'COOP' and "
        "updated > now() - '25 hours'::interval",
        accessdb,
        index_col=None,
    )
    LOG.debug("Found %s database changes", len(df.index))
    return df


def load_xref():
    """Figure out which stations below to whom."""
    dbconn = get_dbconn("mesosite")
    cursor = dbconn.cursor()
    cursor.execute(
        "SELECT id, value from stations t JOIN station_attributes a "
        "on (t.iemid = a.iemid) WHERE t.network ~* 'CLIMATE' and "
        "a.attr = 'TRACKS_STATION' and t.online"
    )
    xref = {}
    for row in cursor:
        entry = xref.setdefault(row[1], [])
        entry.append(row[0])
    return xref


def compare_and_update(ccursor, currentob, newob):
    """Do we need to make updates?"""
    if newob is None:
        return 0
    updates = []
    messages = []
    for col in ["high", "low", "precip", "snow", "snowd"]:
        # If new ob is missing, nothing to do here
        if newob[col] is None:
            continue
        # If obs are the same, nothing to do here
        if newob[col] == currentob[col]:
            continue
        updates.append(f"{col} = {newob[col]}")
        messages.append(f"{col} {currentob[col]}->{newob[col]}")
        if col in ["precip", "high"]:
            updates.append(
                f"{'temp' if col != 'precip' else 'precip'}_estimated = 'f'"
            )
            chour = "null" if pd.isna(newob["chour"]) else newob["chour"]
            updates.append(
                f"{'temp' if col != 'precip' else 'precip'}_hour = {chour}"
            )
    if not updates:
        return 0
    LOG.debug(
        "%s %s %s", currentob["station"], currentob["day"], ", ".join(messages)
    )
    ccursor.execute(
        f"UPDATE alldata_{currentob['station'][:2]} SET {', '.join(updates)} "
        "WHERE station = %s and day = %s",
        (currentob["station"], currentob["day"]),
    )
    return ccursor.rowcount


def main():
    """Go Main Go."""
    accessdb = get_dbconn("iem")
    acursor = accessdb.cursor(cursor_factory=DictCursor)
    coopdb = get_dbconn("coop")
    ccursor = coopdb.cursor(cursor_factory=DictCursor)
    df = load_changes(accessdb)
    xref = load_xref()
    updates = 0
    unused = 0
    dups = 0
    for _, row in df.iterrows():
        key = f"{row['id']}|{row['network']}"
        if key not in xref:
            unused += 1
            continue
        # Load the changed data
        acursor.execute(
            "SELECT max_tmpf::int as high, min_tmpf::int as low, "
            "pday as precip, snow, snowd, "
            "extract(hour from (coop_valid + '1 minute'::interval) at "
            "time zone %s) as chour from summary "
            "WHERE iemid = %s and day = %s",
            (row["tzname"], row["iemid"], row["date"]),
        )
        newob = acursor.fetchone()
        for climostation in xref[key]:
            table = f"alldata_{climostation[:2]}"
            # Load the current data for the station

            def _fetch():
                ccursor.execute(
                    "SELECT high, low, precip, snow, snowd, station, day from "
                    f"{table} WHERE station = %s and day = %s",
                    (climostation, row["date"]),
                )
                return ccursor.fetchone()

            currentob = _fetch()
            if currentob is None:
                ccursor.execute(
                    f"INSERT into {table}(station, day, year, month, sday) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (
                        climostation,
                        row["date"],
                        row["date"].year,
                        row["date"].month,
                        row["date"].strftime("%m%d"),
                    ),
                )
                currentob = _fetch()
            updated = compare_and_update(ccursor, currentob, newob)
            if updated == 0:
                dups += 1
                continue
            updates += updated
            if updates > 0 and updates % 100 == 0:
                LOG.debug("database commit after %s updates", updates)
                ccursor.close()
                coopdb.commit()
                ccursor = coopdb.cursor(cursor_factory=DictCursor)

    LOG.info("synced %s rows, %s unused, %s dups", updates, unused, dups)
    ccursor.close()
    coopdb.commit()


if __name__ == "__main__":
    main()
