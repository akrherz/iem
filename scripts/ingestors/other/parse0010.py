"""ISU Agronomy Hall Vantage Pro 2 OT0010"""
from __future__ import print_function
import datetime
import re
import os
import sys
import pytz
from pyiem.datatypes import speed, temperature, humidity
from pyiem.observation import Observation
from pyiem.meteorology import dewpoint
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    iemaccess = get_dbconn("iem")
    cursor = iemaccess.cursor()

    valid = datetime.datetime.utcnow()
    valid = valid.replace(tzinfo=pytz.utc)
    valid = valid.astimezone(pytz.timezone("America/Chicago"))
    fn = valid.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0010.dat")

    if not os.path.isfile(fn):
        sys.exit(0)

    lines = open(fn, "r").readlines()
    lastline = lines[-1].strip()
    tokens = re.split(r"[\s+]+", lastline)
    if len(tokens) != 20:
        return

    tparts = re.split(":", tokens[3])
    valid = valid.replace(
        hour=int(tparts[0]), minute=int(tparts[1]), second=0, microsecond=0
    )

    iem = Observation("OT0010", "OT", valid)

    iem.data["tmpf"] = float(tokens[4])
    iem.data["max_tmpf"] = float(tokens[5])
    iem.data["min_tmpf"] = float(tokens[6])
    iem.data["relh"] = int(tokens[7])
    iem.data["dwpf"] = dewpoint(
        temperature(iem.data["tmpf"], "F"), humidity(iem.data["relh"], "%")
    ).value("F")
    iem.data["sknt"] = speed(float(tokens[8]), "mph").value("KT")
    iem.data["drct"] = int(tokens[9])
    iem.data["max_sknt"] = speed(float(tokens[10]), "mph").value("KT")
    iem.data["alti"] = float(tokens[12])
    iem.data["pday"] = float(tokens[13])
    iem.data["srad"] = None if tokens[18] == "n/a" else float(tokens[18])

    iem.save(cursor)

    cursor.close()
    iemaccess.commit()


if __name__ == "__main__":
    main()
