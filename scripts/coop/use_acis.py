"""Use data provided by ACIS to replace IEM COOP data."""
import sys
import datetime

import requests
from tqdm import tqdm
from pyiem.observation import Observation
from pyiem.util import get_dbconn, utc, logger
from pyiem.reference import TRACE_VALUE

LOG = logger()
SERVICE = "http://data.rcc-acis.org/StnData"


def safe(val):
    """Hack"""
    if val in ["M", "S"]:
        return None
    if val == "T":
        return TRACE_VALUE
    try:
        return float(val)
    except Exception as exp:
        LOG.info(
            "%s failed to convert %s to float, using None", exp, repr(val)
        )


def main(network, nwsli):
    """Do the query and work

    Args:
      network (str): IEM network identifier
      nwsli (str): NWSLI ID
    """
    payload = {
        "sid": nwsli,
        "sdate": "1850-01-01",
        "edate": "2012-01-01",
        "elems": "obst,maxt,mint,pcpn,snow,snwd",
    }
    req = requests.post(SERVICE, json=payload)
    j = req.json()
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    for row in tqdm(j["data"], disable=not sys.stdout.isatty()):
        date = datetime.datetime.strptime(row[0], "%Y-%m-%d")
        (obst, high, low, precip, snow, snowd) = map(safe, row[1:])
        if all([a is None for a in (obst, high, low, precip, snow, snowd)]):
            continue
        ob = Observation(
            nwsli, network, utc(date.year, date.month, date.day, 12)
        )
        ob.data["max_tmpf"] = high
        ob.data["min_tmpf"] = low
        ob.data["coop_tmpf"] = obst
        ob.data["pday"] = precip
        ob.data["snow"] = snow
        ob.data["snowd"] = snowd
        ob.save(cursor, skip_current=True)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
