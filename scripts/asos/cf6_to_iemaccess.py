"""Merge the CF6 Processed Data.

Run from RUN_12Z.sh for yesterday and a few other previous dates.
"""
# pylint: disable=no-member
# stdlib
import sys
from datetime import date

# third party
from pyiem.util import get_sqlalchemy_conn, get_dbconn, logger
from metpy.units import units
import pandas as pd

LOG = logger()


def comp(old, new):
    """Figure out if this value is new or not."""
    if pd.isnull(new):
        return False
    if pd.isnull(old):
        return True
    if old == new:
        return False
    if abs(new - old) < 0.01:
        return False
    return True


def main(argv):
    """Go Main Go."""
    dbconn = get_dbconn("iem")
    valid = date(int(argv[1]), int(argv[2]), int(argv[3]))
    with get_sqlalchemy_conn("iem") as conn:
        cf6 = pd.read_sql(
            "SELECT * from cf6_data where valid = %s ORDER by station ASC",
            conn,
            params=(valid,),
            index_col="station",
        )
    for col in ["avg_smph", "max_smph", "gust_smph"]:
        cf6[col.replace("smph", "sknt")] = (
            (units("miles/hour") * cf6[col].values).to(units("knots")).m
        )
    LOG.info("Loaded %s CF6 entries for %s date", len(cf6.index), valid)

    table = f"summary_{valid.year}"
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(
            "SELECT s.*, t.network, "
            "case when length(t.id) = 3 then 'K'||t.id else t.id end "
            f"as station from {table} s JOIN "
            "stations t on (s.iemid = t.iemid) WHERE s.day = %s and "
            "t.network ~* 'ASOS' ORDER by station ASC",
            conn,
            params=(valid,),
            index_col="station",
        )

    df = cf6.join(obs, lsuffix="_cf6")
    obscols = (
        "max_tmpf min_tmpf pday snow snowd avg_sknt max_sknt "
        "avg_drct max_gust max_drct"
    ).split()
    cf6cols = (
        "high low precip snow_cf6 snowd_12z avg_sknt_cf6 max_sknt_cf6 "
        "avg_drct gust_sknt gust_drct"
    ).split()
    cursor = dbconn.cursor()
    updated_vals = 0
    updated_rows = 0
    for station, row in df.iterrows():
        if pd.isnull(row["iemid"]):
            # Lots of false positives here, like WFOs
            LOG.info("Yikes, station %s is unknown?", station)
            continue
        work = []
        params = []
        for ocol, ccol in zip(obscols, cf6cols):
            if not comp(row[ocol], row[ccol]):
                continue
            # LOG.debug("%s %s %s->%s", station, ocol, row[ocol], row[ccol])
            updated_vals += 1
            work.append(f"{ocol} = %s")
            params.append(row[ccol])
        if not work:
            continue
        params.append(int(row["iemid"]))
        params.append(valid)
        updated_rows += 1
        cursor.execute(
            f"UPDATE {table} SET {','.join(work)} WHERE iemid = %s and "
            "day = %s",
            params,
        )

    cursor.close()
    dbconn.commit()
    LOG.info("Updated %s values over %s rows", updated_vals, updated_rows)


if __name__ == "__main__":
    main(sys.argv)
