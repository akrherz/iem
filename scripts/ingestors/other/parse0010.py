"""ISU Agronomy Hall Vantage Pro 2 OT0010"""
import os
import re
import sys
from zoneinfo import ZoneInfo

from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from pyiem.observation import Observation
from pyiem.util import convert_value, get_dbconnc, logger, utc

LOG = logger()


def main():
    """Go Main Go"""
    iemaccess, cursor = get_dbconnc("iem")

    valid = utc().astimezone(ZoneInfo("America/Chicago"))
    fn = valid.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/text/ot/ot0010.dat")

    if not os.path.isfile(fn):
        LOG.info("missing %s", fn)
        sys.exit(0)

    with open(fn, encoding="ascii") as fh:
        lines = fh.readlines()
    lastline = lines[-1].strip()
    tokens = re.split(r"[\s+]+", lastline)
    if len(tokens) != 19:
        return

    tparts = re.split(":", tokens[3])
    valid = valid.replace(
        hour=int(tparts[0]), minute=int(tparts[1]), second=0, microsecond=0
    )

    iem = Observation("OT0010", "OT", valid)

    iem.data["tmpf"] = float(tokens[4])
    iem.data["max_tmpf"] = float(tokens[5])
    iem.data["min_tmpf"] = float(tokens[6])
    relh = int(tokens[7])
    if 0 < relh <= 100:
        iem.data["relh"] = int(tokens[7])
        iem.data["dwpf"] = (
            dewpoint_from_relative_humidity(
                units("degF") * iem.data["tmpf"],
                units("percent") * iem.data["relh"],
            )
            .to(units("degF"))
            .m
        )
    else:
        LOG.debug("relative humidity out of bounds: %s", relh)
    iem.data["sknt"] = convert_value(float(tokens[7]), "mile / hour", "knot")
    iem.data["drct"] = int(tokens[8])
    iem.data["max_sknt"] = convert_value(
        float(tokens[9]), "mile / hour", "knot"
    )
    iem.data["alti"] = float(tokens[11])
    iem.data["pday"] = float(tokens[13]) / 100.0
    iem.data["srad"] = float(tokens[18])

    iem.save(cursor)

    cursor.close()
    iemaccess.commit()


if __name__ == "__main__":
    main()
