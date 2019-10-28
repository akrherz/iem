"""Check autoplot stats"""
from __future__ import print_function
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("mesosite", user="nobody")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        select count(*), avg(timing) from autoplot_timing
        where valid > now() - '4 hours'::interval
    """
    )
    (count, speed) = cursor.fetchone()
    speed = 0 if speed is None else speed

    print(
        ("Autoplot cnt:%s speed:%.2f | COUNT=%s;; SPEED=%.3f;;")
        % (count, speed, count, speed)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
