"""Quick and Dirty to get the ISUMET station data into the DB"""
import re
import os
import sys

import pytz
from pyiem.observation import Observation
from pyiem.util import get_dbconn, utc, convert_value


def main():
    """Go Main Go"""
    iemaccess = get_dbconn("iem")
    cursor = iemaccess.cursor()
    valid = utc().astimezone(pytz.timezone("America/Chicago"))
    fn = valid.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0002.dat")

    if not os.path.isfile(fn):
        sys.exit()

    with open(fn, "r", encoding="ascii") as fh:
        lines = fh.readlines()
    lastline = lines[-1]
    tokens = re.split(r"[\s+]+", lastline)

    tparts = re.split(":", tokens[4])
    valid = valid.replace(
        hour=int(tparts[0]), minute=int(tparts[1]), second=int(tparts[2])
    )

    iem = Observation("OT0002", "OT", valid)

    sknt = convert_value(float(tokens[8]), "mile / hour", "knot")

    iem.data["sknt"] = sknt
    iem.data["drct"] = tokens[9]
    iem.data["tmpf"] = tokens[7]

    iem.save(cursor)

    cursor.close()
    iemaccess.commit()


if __name__ == "__main__":
    main()
