"""Quick and Dirty to get the ISUMET station data into the DB"""
import re
import os
import sys

import pytz
from pyiem.datatypes import speed
from pyiem.observation import Observation
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go"""
    iemaccess = get_dbconn("iem")
    cursor = iemaccess.cursor()
    valid = utc().astimezone(pytz.timezone("America/Chicago"))
    fn = valid.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0002.dat")

    if not os.path.isfile(fn):
        sys.exit(0)

    lines = open(fn, "r").readlines()
    lastline = lines[-1]
    tokens = re.split(r"[\s+]+", lastline)

    tparts = re.split(":", tokens[4])
    valid = valid.replace(
        hour=int(tparts[0]), minute=int(tparts[1]), second=int(tparts[2])
    )

    iem = Observation("OT0002", "OT", valid)

    sknt = speed(float(tokens[8]), "MPH").value("KT")

    iem.data["sknt"] = sknt
    iem.data["drct"] = tokens[9]
    iem.data["tmpf"] = tokens[7]

    iem.save(cursor)

    cursor.close()
    iemaccess.commit()


if __name__ == "__main__":
    main()
