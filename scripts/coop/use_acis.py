"""Use data provided by ACIS to replace IEM COOP data."""

import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
import httpx
import pandas as pd
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.observation import Observation
from pyiem.reference import TRACE_VALUE
from pyiem.util import logger
from tqdm import tqdm

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
        LOG.warning(
            "%s failed to convert %s to float, using None", exp, repr(val)
        )
    return None


def is_new(newval, oldval):
    """Is this new value new?"""
    if pd.isna(newval):
        return False
    if pd.isna(oldval):
        return True
    if newval == oldval:
        return False
    return True


@click.command()
@click.option("--state")
@click.option("--station", default=None)
def main(state, station):
    """Run for a given state."""
    network = f"{state}_COOP"
    # We are only asking for the last 720 days of data, so might as well only
    # do stations that are currently known to be `online`
    nt = NetworkTable(network, only_online=station is None)
    ets = date.today() - timedelta(days=1)
    sts = ets - timedelta(days=720)
    pgconn, cursor = get_dbconnc("iem")
    # Lame for now
    cursor.close()
    ids = nt.sts.keys() if station is None else [station]
    progress = tqdm(ids, total=len(ids), disable=not sys.stdout.isatty())
    for nwsli in progress:
        progress.set_description(nwsli)
        tz = ZoneInfo(nt.sts[nwsli]["tzname"])
        with get_sqlalchemy_conn("iem") as conn:
            obsdf = pd.read_sql(
                "SELECT day, max_tmpf as maxt, min_tmpf as mint, "
                "pday as pcpn, snow, snowd as snwd, coop_tmpf as obst "
                "from summary WHERE iemid = %s and day >= %s and day <= %s "
                "ORDER by day ASC",
                conn,
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
            resp = httpx.post(SERVICE, json=payload, timeout=30)
            resp.raise_for_status()
            j = resp.json()
        except Exception as exp:
            LOG.warning("download and processing failed for %s", nwsli)
            LOG.exception(exp)
            continue
        cursor = pgconn.cursor()
        if "data" not in j:
            LOG.warning("Did not get data for %s ACIS request", nwsli)
            continue
        updates = 0
        for row in j["data"]:
            dt = datetime.strptime(row[0], "%Y-%m-%d")
            data = {}
            hour = None
            current = obsdf.loc[dt]
            for i, col in enumerate("obst maxt mint pcpn snow snwd".split()):
                val = safe(row[i + 1][0])
                if not is_new(val, current[col]):
                    continue
                data[col] = val
                if hour is None:
                    hour = row[i + 1][1]
            if not data or hour < 0:
                continue
            valid = datetime(
                dt.year,
                dt.month,
                dt.day,
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
            LOG.warning("Updated %s rows for %s", updates, nwsli)
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
