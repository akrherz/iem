"""Use data provided by ACIS to replace climodat data."""
import sys
import datetime
import time

import requests
import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, get_dbconnstr, logger, exponential_backoff
from pyiem.reference import TRACE_VALUE, ncei_state_codes

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnData"


def safe(val):
    """Hack"""
    if pd.isnull(val):
        return None
    if val in ["M", "S"]:
        return None
    if val == "T":
        return TRACE_VALUE
    # Multi-day we can't support
    if isinstance(val, str) and val.endswith("A"):
        return None
    try:
        return float(val)
    except ValueError:
        LOG.info("failed to convert %s to float, using None", repr(val))


def compare(row, colname):
    """Do we need to update this column?"""
    oldval = safe(row[colname])
    newval = safe(row[f"a{colname}"])
    if oldval is None and newval is not None:
        return True
    if newval is not None and oldval != newval:
        return True
    return False


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
            {"name": "mint", "add": "t"},
            {"name": "pcpn", "add": "t"},
            {"name": "snow", "add": "t"},
            {"name": "snwd", "add": "t"},
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
    for col in "ahigh alow aprecip asnow asnowd".split():
        acis[[col, f"{col}_hour"]] = pd.DataFrame(
            acis[col].tolist(),
            index=acis.index,
        )
    LOG.info("Loaded %s rows from ACIS", len(acis.index))
    acis["day"] = pd.to_datetime(acis["day"])
    acis = acis.set_index("day")
    pgconn = get_dbconn("coop")
    obs = pd.read_sql(
        f"SELECT day, high, low, precip, snow, snowd from {table} WHERE "
        "station = %s ORDER by day ASC",
        get_dbconnstr("coop"),
        params=(station,),
        index_col="day",
    )
    LOG.info("Loaded %s rows from IEM", len(obs.index))
    obs["dbhas"] = 1
    cursor = pgconn.cursor()
    # join the tables
    df = acis.join(obs, how="left")
    inserts = 0
    updates = 0
    minday = None
    maxday = None
    for day, row in df.iterrows():
        work = []
        args = []
        for col in ["high", "low", "precip", "snow", "snowd"]:
            if not compare(row, col):
                continue
            work.append(f"{col} = %s")
            args.append(safe(row[f"a{col}"]))
            if col in ["high", "precip"]:
                work.append(
                    f"{'temp' if col == 'high' else 'precip'}_hour = %s"
                )
                work.append(
                    f"{'temp' if col == 'high' else 'precip'}_estimated = 'f'"
                )
                args.append(row[f"a{col}_hour"])
        if not work:
            continue
        if minday is None:
            minday = day
        maxday = day
        if row["dbhas"] != 1:
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
        updates += 1

    if minday is not None:
        LOG.warning(
            "%s[%s %s] Updates: %s Inserts: %s",
            station,
            minday.date(),
            maxday.date(),
            updates,
            inserts,
        )
    cursor.close()
    pgconn.commit()
    return updates


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
                if sid[2] in ["T", "C"] or sid[2:] == "0000":
                    continue
                acis_station = ncei_state_codes[arg] + sid[2:]
                _worker(sid, acis_station)
        else:
            station = arg
            acis_station = ncei_state_codes[station[:2]] + station[2:]
            _worker(station, acis_station)
    else:
        (station, acis_station) = argv[1], argv[2]
        _worker(station, acis_station)


if __name__ == "__main__":
    main(sys.argv)
