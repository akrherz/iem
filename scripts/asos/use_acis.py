"""
Sync ACIS content to IEM Access for the ASOS sites.
"""
import datetime
import sys
import time

import pandas as pd
import requests
from pyiem.network import Table as NetworkTable
from pyiem.reference import TRACE_VALUE
from pyiem.util import (
    exponential_backoff,
    get_dbconn,
    get_sqlalchemy_conn,
    logger,
)

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnData"


def safe(val):
    """Hack"""
    if pd.isnull(val):
        return None
    # Multi-day we can't support
    if isinstance(val, str) and val.endswith("A"):
        return None
    try:
        return float(val)
    except ValueError:
        LOG.info("failed to convert %s to float, using None", repr(val))
    return None


def compare(row, colname):
    """Do we need to update this column?"""
    oldval = safe(row[colname])
    newval = safe(row[f"a{colname}"])
    if newval is not None and colname in ["high", "low", "precip"]:
        # If we have an estimated flag and ACIS is not None, do things.
        if row[f"{'precip' if colname == 'precip' else 'temp'}_estimated"]:
            return newval
    if oldval is None and newval is not None:
        return newval
    if newval is not None and oldval != newval:
        return newval
    return None


def do(meta, acis_station, interactive):
    """Do the query and work"""
    today = datetime.date.today()
    fmt = "%Y-%m-%d"
    payload = {
        "sid": acis_station,
        "sdate": meta["attributes"].get(
            "FLOOR", meta["archive_begin"].strftime("%Y-%m-%d")
        ),
        "edate": meta["attributes"].get("CEILING", today.strftime(fmt)),
        "elems": [
            {"name": "maxt", "add": "t"},
            {"name": "mint"},
            {"name": "pcpn", "add": "t"},
        ],
    }
    if not interactive:
        payload["sdate"] = (today - datetime.timedelta(days=365)).strftime(fmt)
    LOG.info(
        "Call ACIS for: %s[%s %s]",
        acis_station,
        payload["sdate"],
        payload["edate"],
    )
    req = exponential_backoff(requests.post, SERVICE, json=payload, timeout=30)
    if req is None:
        LOG.warning("Total download failure for %s", acis_station)
        return 0
    if req.status_code != 200:
        LOG.warning("Got status_code %s for %s", req.status_code, acis_station)
        # Give server some time to recover from transient errors
        time.sleep(60)
        return 0
    try:
        j = req.json()
    except Exception as exp:
        LOG.exception(exp)
        return 0
    if "data" not in j:
        LOG.info("No Data!, content=%s", req.content)
        return 0
    acis = pd.DataFrame(
        j["data"],
        columns="day amax_tmpf amin_tmpf apday".split(),
    )
    for col in "amax_tmpf apday".split():
        acis[[col, f"{col}_hour"]] = pd.DataFrame(
            acis[col].tolist(),
            index=acis.index,
        )
        # hour values of -1 are missing
        acis.loc[acis[f"{col}_hour"] < 0, f"{col}_hour"] = pd.NA
    # Rectify the name to match IEM database
    acis = acis.rename(columns={"amax_tmpf_hour": "atemp_hour"}).replace(
        {"T": TRACE_VALUE, "M": pd.NA, "S": pd.NA}
    )

    LOG.info("Loaded %s rows from ACIS", len(acis.index))
    acis["day"] = pd.to_datetime(acis["day"])
    acis = acis.set_index("day")
    pgconn = get_dbconn("iem")
    with get_sqlalchemy_conn("iem") as conn:
        obs = pd.read_sql(
            """
            SELECT day, max_tmpf, min_tmpf, pday
            from summary WHERE iemid = %s ORDER by day ASC
            """,
            conn,
            params=(meta["iemid"],),
            index_col="day",
        )
        obs["dbhas"] = True
    LOG.info("Loaded %s rows from IEM", len(obs.index))
    cursor = pgconn.cursor()
    # join the tables
    df = acis.join(obs, how="left")
    df["dbhas"] = df["dbhas"].fillna(False).infer_objects(copy=False)
    inserts = 0
    updates = {}
    minday = None
    maxday = None
    cols = "max_tmpf min_tmpf pday".split()
    for col in cols:
        updates[col] = 0
    for day, row in df.iterrows():
        work = []
        args = []
        for col in cols:
            newval = compare(row, col)
            if newval is None:
                continue
            work.append(f"{col} = %s")
            args.append(newval)
            if row["dbhas"]:
                updates[col] += 1
        if not work:
            continue
        if minday is None:
            minday = day
        maxday = day
        if not row["dbhas"]:
            inserts += 1
            cursor.execute(
                "INSERT into summary (iemid, day) VALUES (%s, %s)",
                (meta["iemid"], day),
            )
        cursor.execute(
            f"UPDATE summary_{day.year} SET {','.join(work)} "
            "WHERE iemid = %s and day = %s",
            (*args, meta["iemid"], day),
        )

    uu = [
        updates["max_tmpf"],
        updates["min_tmpf"],
        updates["pday"],
    ]
    if minday is not None:
        LOG.warning(
            "%s[%s %s] New:%s Updates H:%s L:%s P:%s",
            acis_station,
            minday.date(),
            maxday.date(),
            inserts,
            *uu,
        )
    cursor.close()
    pgconn.commit()
    return max(uu)


def main(argv):
    """Do what is asked."""
    interactive = sys.stdout.isatty()
    state = argv[1]
    # Only run cron job for online sites
    nt = NetworkTable(f"{state}_ASOS", only_online=not interactive)

    for sid in nt.sts:
        if nt.sts[sid]["archive_begin"] is None:
            continue
        updates = do(nt.sts[sid], sid, interactive)
        # If we found a lot of updates over the previous year, rerun for all
        if not interactive and updates > 100:
            do(nt.sts[sid], sid, True)


if __name__ == "__main__":
    main(sys.argv)
