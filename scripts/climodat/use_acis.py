"""Use data provided by ACIS to replace climodat data."""
import sys
import datetime

import requests
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger
from pyiem.reference import TRACE_VALUE

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


def main(argv):
    """Do the query and work

    Args:
      station (str): IEM Station identifier ie IA0200
      acis_station (str): the ACIS identifier ie 130197
    """
    (station, acis_station) = argv[1], argv[2]
    table = "alldata_%s" % (station[:2],)
    payload = {
        "sid": acis_station,
        "sdate": "1850-01-01",
        "edate": datetime.date.today().strftime("%Y-%m-%d"),
        "elems": "maxt,mint,pcpn,snow,snwd",
    }
    LOG.debug("Call ACIS server for: %s to update: %s", acis_station, station)
    req = requests.post(SERVICE, json=payload)
    j = req.json()
    acis = pd.DataFrame(
        j["data"],
        columns=["day", "ahigh", "alow", "aprecip", "asnow", "asnowd"],
    )
    LOG.debug("Loaded %s rows from ACIS", len(acis.index))
    acis["day"] = pd.to_datetime(acis["day"])
    acis = acis.set_index("day")
    pgconn = get_dbconn("coop")
    obs = read_sql(
        f"SELECT day, high, low, precip, snow, snowd from {table} WHERE "
        "station = %s ORDER by day ASC",
        pgconn,
        params=(station,),
        index_col="day",
    )
    LOG.debug("Loaded %s rows from IEM", len(obs.index))
    obs["dbhas"] = 1
    cursor = pgconn.cursor()
    # join the tables
    df = acis.join(obs, how="left")
    inserts = 0
    updates = 0
    for day, row in df.iterrows():
        work = []
        args = []
        for col in ["high", "low", "precip", "snow", "snowd"]:
            if compare(row, col):
                work.append(f"{col} = %s")
                args.append(safe(row[f"a{col}"]))
        if not work:
            continue
        if row["dbhas"] != 1:
            inserts += 1
            cursor.execute(
                f"INSERT into {table} (station, day, sday, year, month) "
                "VALUES (%s, %s, %s, %s, %s)",
                (station, day, day.strftime("%m%d"), day.year, day.month),
            )
        LOG.debug("%s -> %s %s", day, work, args)
        cursor.execute(
            f"UPDATE {table} SET {','.join(work)} WHERE station = %s and "
            "day = %s",
            (*args, station, day),
        )
        updates += 1

    LOG.info("Updates: %s Inserts: %s", updates, inserts)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
