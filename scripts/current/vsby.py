"""Generate analysis of visibility."""

from datetime import datetime, timezone

import click
from pyiem.util import logger, utc, web2ldm

LOG = logger()


@click.command()
@click.option("--valid", type=click.DateTime(), help="UTC valid time")
def main(valid: datetime | None):
    """GO!"""
    if valid is not None:
        valid = valid.replace(tzinfo=timezone.utc)
        routes = "a"
    else:
        valid = utc()
        routes = "ac"
    pqstr = (
        f"plot {routes} {valid:%Y%m%d%H}00 iowa_vsby.png "
        f"vsby_countour_{valid:%H}.png png"
    )
    url = (
        "https://mesonet.agron.iastate.edu/plotting/auto/plot/192/"
        f"valid:{valid:%Y-%m-%d%%20%H}00::"
        "t:state::state:IA::v:vsby::cmap:gray::_cb:1.png"
    )
    LOG.info("%s -> %s", url, pqstr)
    web2ldm(url, pqstr)


if __name__ == "__main__":
    main()
