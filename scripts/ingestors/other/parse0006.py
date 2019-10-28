"""Hacky parsers"""
import datetime
import os
import sys

import pytz
from pyiem.observation import Observation
from pyiem.datatypes import speed
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    now = datetime.datetime.now().replace(
        tzinfo=pytz.timezone("America/Chicago")
    )

    fn = ("/mesonet/ARCHIVE/data/%s/text/ot/ot0006.dat" "") % (
        now.strftime("%Y/%m/%d"),
    )

    if not os.path.isfile(fn):
        return
    lines = open(fn, "r").readlines()
    line = lines[-1]

    # January 17, 2017 02:57 PM
    # 35.1 35.8 33.4 92 3 351 14 2:13PM 30.03 0.00 1.12 1.12 68.6 36
    tokens = line.split(" ")
    if len(tokens) != 19:
        sys.exit(0)

    ts = datetime.datetime.strptime(" ".join(tokens[:5]), "%B %d, %Y %I:%M %p")

    ts = now.replace(
        year=ts.year,
        month=ts.month,
        day=ts.day,
        hour=ts.hour,
        minute=ts.minute,
    )

    iemob = Observation("OT0006", "OT", ts)

    iemob.data["tmpf"] = float(tokens[5])
    iemob.data["relh"] = float(tokens[8])
    iemob.data["sknt"] = speed(float(tokens[9]), "MPH").value("KT")
    iemob.data["drct"] = tokens[10]
    iemob.data["alti"] = float(tokens[13])
    iemob.data["pday"] = float(tokens[14])
    iemob.save(icursor)

    icursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
