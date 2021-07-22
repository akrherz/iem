"""Use data provided by ACIS to replace IEM COOP data."""
import sys
import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

import requests
from tqdm import tqdm
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem.util import get_dbconn, logger
from pyiem.reference import TRACE_VALUE

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnData"


def safe(val):
    """Hack"""
    if val.endswith("A"):  # unsure
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
    except Exception as exp:
        LOG.info(
            "%s failed to convert %s to float, using None", exp, repr(val)
        )


def is_new(newval, oldval):
    """Is this new value new?"""
    if pd.isna(newval):
        return False
    if pd.isna(oldval):
        return True
    if newval == oldval:
        return False
    return True


def main(argv):
    """Run for a given state."""
    state = argv[1]
    network = f"{state}_COOP"
    # We are only asking for the last 720 days of data, so might as well only
    # do stations that are currently known to be `online`
    nt = NetworkTable(network, only_online=True)
    ets = datetime.date.today() - datetime.timedelta(days=1)
    sts = ets - datetime.timedelta(days=720)
    pgconn = get_dbconn("iem")
    progress = tqdm(nt.sts, total=len(nt.sts), disable=not sys.stdout.isatty())
    for nwsli in progress:
        progress.set_description(nwsli)
        tz = ZoneInfo(nt.sts[nwsli]["tzname"])
        obsdf = read_sql(
            "SELECT day, max_tmpf as maxt, min_tmpf as mint, "
            "pday as pcpn, snow, snowd as snwd, coop_tmpf as obst "
            "from summary WHERE iemid = %s and day >= %s and day <= %s "
            "ORDER by day ASC",
            pgconn,
            params=(nt.sts[nwsli]["iemid"], sts, ets),
            index_col="day",
        )
        obsdf = obsdf.reindex(pd.date_range(sts, ets))
        payload = {
            "sid": nwsli,
            "sdate": sts.strftime("%Y-%m-%d"),
            "edate": ets.strftime("%Y-%m-%d"),
            "elems": [
                {"name": "obst", "add": "t"},
                {"name": "maxt", "add": "t"},
                {"name": "mint", "add": "t"},
                {"name": "pcpn", "add": "t"},
                {"name": "snow", "add": "t"},
                {"name": "snwd", "add": "t"},
            ],
        }
        try:
            req = requests.post(SERVICE, json=payload, timeout=30)
            j = req.json()
        except Exception as exp:
            LOG.info("download and processing failed for %s", nwsli)
            LOG.exception(exp)
            continue
        cursor = pgconn.cursor()
        if "data" not in j:
            LOG.info("Did not get data for %s ACIS request", nwsli)
            continue
        updates = 0
        for row in j["data"]:
            date = datetime.datetime.strptime(row[0], "%Y-%m-%d")
            data = {}
            hour = None
            current = obsdf.loc[date]
            for i, col in enumerate("obst maxt mint pcpn snow snwd".split()):
                val = safe(row[i + 1][0])
                if not is_new(val, current[col]):
                    continue
                data[col] = val
                if hour is None:
                    hour = row[i + 1][1]
            if not data:
                continue
            valid = datetime.datetime(
                date.year,
                date.month,
                date.day,
                hour if hour < 24 else 23,
                0 if hour < 24 else 59,
                tzinfo=tz,
            )
            ob = Observation(nwsli, network, valid)
            ob.data["coop_valid"] = valid
            if "maxt" in data:
                ob.data["max_tmpf"] = data["maxt"]
            if "mint" in data:
                ob.data["min_tmpf"] = data["mint"]
            if "obst" in data:
                ob.data["coop_tmpf"] = data["obst"]
            if "pcpn" in data:
                ob.data["pday"] = data["pcpn"]
            if "snow" in data:
                ob.data["snow"] = data["snow"]
            if "snwd" in data:
                ob.data["snowd"] = data["snwd"]
            ob.save(cursor, skip_current=True)
            updates += 1
        if updates > 0:
            LOG.info("Updated %s rows for %s", updates, nwsli)
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
