"""High Temperature.

RUN_10MIN.sh
"""

from datetime import date
from typing import Optional

import click
from pyiem.util import web2ldm


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), default=None, help="Date to plot"
)
def main(dt: Optional[date]):
    """Go Main Go"""
    if dt is None:
        dt = date.today()
        mode = "ac"
    else:
        dt = dt.date()
        mode = "a"

    url = (
        "http://iem.local/plotting/auto/plot/206/t:state::state:IA::"
        f"v:max_tmpf::p:both::day:{dt:%Y-%m-%d}::cmap:jet::_r:43::_cb:1.png"
    )
    pqstr = (
        f"plot {mode} {dt:%Y%m%d0000} summary/iowa_asos_high.png "
        "iowa_asos_high.png png"
    )
    web2ldm(url, pqstr)


if __name__ == "__main__":
    main()
