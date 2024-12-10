"""Quick and Dirty to get the ISUMET station data into the DB"""

import os
import re
import sys
from zoneinfo import ZoneInfo

from pyiem.database import get_dbconnc
from pyiem.observation import Observation
from pyiem.util import convert_value, utc


def main():
    """Go Main Go"""
    valid = utc().astimezone(ZoneInfo("America/Chicago"))
    fn = valid.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0002.dat")

    if not os.path.isfile(fn):
        sys.exit()

    with open(fn, encoding="ascii") as fh:
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

    iemaccess, cursor = get_dbconnc("iem")
    iem.save(cursor)
    cursor.close()
    iemaccess.commit()


if __name__ == "__main__":
    main()
