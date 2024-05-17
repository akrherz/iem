"""Generate a plot of GDD for the ASOS network"""

import datetime

import click
from pyiem.util import logger, web2ldm

LOG = logger()


@click.command()
@click.option("--gddbase", default=50, type=int, help="GDD Base Temperature")
def main(gddbase):
    """Go Main Go"""
    now = datetime.date.today() - datetime.timedelta(days=1)
    jan1 = now.replace(month=1, day=1)

    url = (
        "http://iem.local/plotting/auto/plot/97/d:sector::sector:IA::"
        f"var:gdd_sum::gddbase:{gddbase}::gddceil:86::"
        f"date1:{jan1.strftime('%Y-%m-%d')}::usdm:no::_cb:1::"
        f"date2:{now.strftime('%Y-%m-%d')}::p:contour::cmap:RdBu_r::c:yes"
        ".png"
    )
    name = "gdd" if gddbase == 50 else f"gdd{gddbase}"
    pqstr = f"plot c 000000000000 summary/{name}_jan1.png bogus png"
    LOG.info(url)
    LOG.info(pqstr)
    res = web2ldm(url, pqstr)
    if not res:
        LOG.warning("failed for gddbase: %s", gddbase)


if __name__ == "__main__":
    main()
