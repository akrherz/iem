"""
  Check to make sure the station metadata is reasonable!
called from RUN_MIDNIGHT.sh
"""

from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def main():
    """Go Main"""
    mcursor = get_dbconn("mesosite").cursor()

    mcursor.execute(
        "SELECT id, network, ST_x(geom), ST_y(geom), modified from stations "
        "WHERE ST_x(geom) >= 180 or ST_x(geom) <= -180 or ST_y(geom) > 90 "
        "or ST_y(geom) < -90"
    )
    for row in mcursor:
        LOG.warning("QC FAIL %s %s %s %s %s", *row)


if __name__ == "__main__":
    main()
