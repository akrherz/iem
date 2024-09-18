"""
Create a plot of minimum wind chill

Run from RUN_10_AFTER.sh
"""

from datetime import datetime

import click
from pyiem.util import web2ldm


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
@click.option("--realtime", is_flag=True, default=False)
def main(dt: datetime, realtime: bool):
    """Main Method"""
    routes = "ac" if realtime else "a"
    pqstr = (
        f"plot {routes} {dt:%Y%m%d%H}00 summary/iowa_min_windchill.png "
        "summary/iowa_min_windchill.png png"
    )
    web2ldm(
        (
            "https://mesonet.agron.iastate.edu/plotting/auto/plot/206/t:state"
            f"::state:IA::v:min_feel::p:plot2::day:{dt:%Y-%m-%d}::_r:43::"
            "_cb:1.png"
        ),
        pqstr,
    )


if __name__ == "__main__":
    main()
