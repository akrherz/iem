"""Use data provided by ACIS to replace climodat data."""
import datetime
import sys
import time

import pandas as pd
import requests
from pyiem.network import Table as NetworkTable
from pyiem.reference import TRACE_VALUE, ncei_state_codes
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


def do(meta, station, acis_station, interactive):
    """Do the query and work

    Args:
      station (str): IEM Station identifier ie IA0200
      acis_station (str): the ACIS identifier ie 130197
    """
    table = f"alldata_{station[:2]}"
    today = datetime.date.today()
    fmt = "%Y-%m-%d"
    payload = {
        "sid": acis_station,
        "sdate": meta["attributes"].get("FLOOR", "1850-01-01"),
        "edate": meta["attributes"].get("CEILING", today.strftime(fmt)),
        "elems": [
            {"name": "maxt", "add": "t"},
            {"name": "mint"},
            {"name": "pcpn", "add": "t"},
            {"name": "snow"},
            {"name": "snwd"},
        ],
    }
    if not interactive:
        payload["sdate"] = (today - datetime.timedelta(days=365)).strftime(fmt)
    LOG.info(
        "Call ACIS for: %s[%s %s] to update: %s",
        acis_station,
        payload["sdate"],
        payload["edate"],
        station,
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
        columns="day ahigh alow aprecip asnow asnowd".split(),
    )
    for col in "ahigh aprecip".split():
        acis[[col, f"{col}_hour"]] = pd.DataFrame(
            acis[col].tolist(),
            index=acis.index,
        )
        # hour values of -1 are missing
        acis.loc[acis[f"{col}_hour"] < 0, f"{col}_hour"] = pd.NA
    # Rectify the name to match IEM database
    acis = acis.rename(columns={"ahigh_hour": "atemp_hour"}).replace(
        {"T": TRACE_VALUE, "M": pd.NA, "S": pd.NA}
    )

    LOG.info("Loaded %s rows from ACIS", len(acis.index))
    acis["day"] = pd.to_datetime(acis["day"])
    acis = acis.set_index("day")
    pgconn = get_dbconn("coop")
    with get_sqlalchemy_conn("coop") as conn:
        obs = pd.read_sql(
            """
            SELECT day, high, low, precip, snow, snowd, temp_hour, precip_hour,
            temp_estimated, precip_estimated
            from alldata WHERE station = %s ORDER by day ASC
            """,
            conn,
            params=(station,),
            index_col="day",
        )
        obs["dbhas"] = True
    LOG.info("Loaded %s rows from IEM", len(obs.index))
    cursor = pgconn.cursor()
    # join the tables
    df = acis.join(obs, how="left")
    df["dbhas"] = df["dbhas"].fillna(False)
    inserts = 0
    updates = {}
    minday = None
    maxday = None
    cols = "high low precip snow snowd temp_hour precip_hour".split()
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
            if col in ["high", "precip"]:  # suboptimal to exclude low
                work.append(
                    f"{'precip' if col == 'precip' else 'temp'}_"
                    "estimated = 'f'"
                )
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
                f"INSERT into {table} (station, day, sday, year, month) "
                "VALUES (%s, %s, %s, %s, %s)",
                (station, day, day.strftime("%m%d"), day.year, day.month),
            )
        cursor.execute(
            f"UPDATE {table} SET {','.join(work)} WHERE station = %s and "
            "day = %s",
            (*args, station, day),
        )

    uu = [
        updates["high"],
        updates["temp_hour"],
        updates["low"],
        updates["precip"],
        updates["precip_hour"],
        updates["snow"],
        updates["snowd"],
    ]
    if minday is not None:
        LOG.warning(
            "%s[%s %s] New:%s Updates H:%s HH:%s L:%s P:%s PH:%s S:%s D:%s",
            station,
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
    arg = argv[1]
    # Only run cron job for online sites
    nt = NetworkTable(f"{arg[:2]}CLIMATE", only_online=not interactive)

    def _worker(sid, acis_station):
        """Do work."""
        updates = do(nt.sts[sid], sid, acis_station, interactive)
        # If we found a lot of updates over the previous year, rerun for all
        if not interactive and updates > 100:
            do(nt.sts[sid], sid, acis_station, True)

    if len(argv) == 2:
        if len(arg) == 2:
            for sid in nt.sts:
                if sid[2] == "C" or sid[2:] == "0000":
                    continue
                acis_station = ncei_state_codes[arg] + sid[2:]
                if sid[2] in ["K", "P"]:
                    acis_station = sid[2:]
                if sid[2] == "T":
                    acis_station = f"{sid[3:]}thr"
                _worker(sid, acis_station)
        else:
            station = arg
            acis_station = ncei_state_codes[station[:2]] + station[2:]
            if station[2] in ["K", "P"]:
                acis_station = station[2:]
            if station[2] == "T":
                acis_station = f"{station[3:]}thr"
            _worker(station, acis_station)
    else:
        (station, acis_station) = argv[1], argv[2]
        _worker(station, acis_station)


if __name__ == "__main__":
    main(sys.argv)
