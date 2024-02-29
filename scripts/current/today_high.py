"""High Temperature.

RUN_10MIN.sh
"""

import datetime
import sys

from pyiem.util import web2ldm


def main(argv):
    """Go Main Go"""
    now = datetime.date.today()
    mode = "ac"
    if len(argv) == 4:
        now = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
        mode = "a"

    url = (
        "http://iem.local/plotting/auto/plot/206/t:state::state:IA::"
        f"v:max_tmpf::p:both::day:{now:%Y-%m-%d}::cmap:jet::_r:43::_cb:1.png"
    )
    pqstr = (
        f"plot {mode} {now:%Y%m%d0000} summary/iowa_asos_high.png "
        "iowa_asos_high.png png"
    )
    web2ldm(url, pqstr)


if __name__ == "__main__":
    main(sys.argv)
