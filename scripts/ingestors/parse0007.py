"""Ingestor"""
import datetime
import os
import sys

import pytz
from pyiem.observation import Observation
import pyiem.meteorology as meteorology
from pyiem.datatypes import temperature, humidity
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    now = datetime.datetime.now()

    fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0007.dat")

    if not os.path.isfile(fn):
        sys.exit(0)

    lines = open(fn, "r").readlines()
    line = lines[-1]

    # 114,2006,240,1530,18.17,64.70, 88.9,2.675,21.91,1014.3,0.000
    tokens = line.split(",")
    if len(tokens) != 11:
        sys.exit(0)
    hhmm = "%04i" % (int(tokens[3]),)
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
    tmpf = temperature(iemob.data["tmpf"], "F")
    relh = humidity(iemob.data["relh"], "%")
    iemob.data["dwpf"] = meteorology.dewpoint(tmpf, relh).value("F")
    iemob.data["sknt"] = float(tokens[7]) * 1.94
    iemob.data["drct"] = tokens[8]
    iemob.data["pres"] = float(tokens[9]) / 960 * 28.36
    iemob.save(icursor)

    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
