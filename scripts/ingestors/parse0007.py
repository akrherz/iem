"""Ingestor"""
import datetime
import os
import sys

import pytz
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from pyiem.observation import Observation
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    now = datetime.datetime.now()

    fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0007.dat")

    if not os.path.isfile(fn):
        LOG.info("Missing %s", fn)
        sys.exit(0)

    with open(fn, "r", encoding="ascii") as fh:
        lines = fh.readlines()
    line = lines[-1]

    # 114,2006,240,1530,18.17,64.70, 88.9,2.675,21.91,1014.3,0.000
    tokens = line.split(",")
    if len(tokens) != 11:
        sys.exit(0)
    hhmm = f"{int(tokens[3]):04.0f}"
    ts = now.replace(
        hour=int(hhmm[:2]),
        minute=int(hhmm[2:]),
        second=0,
        microsecond=0,
        tzinfo=pytz.timezone("America/Chicago"),
    )

    iemob = Observation("OT0007", "OT", ts)

    iemob.data["tmpf"] = float(tokens[5])
    iemob.data["relh"] = float(tokens[6])
    tmpf = units("degF") * iemob.data["tmpf"]
    relh = units("percent") * iemob.data["relh"]
    iemob.data["dwpf"] = (
        dewpoint_from_relative_humidity(tmpf, relh).to(units("degF")).m
    )
    iemob.data["sknt"] = float(tokens[7]) * 1.94
    iemob.data["drct"] = tokens[8]
    iemob.data["pres"] = float(tokens[9]) / 960 * 28.36
    iemob.save(icursor)

    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
