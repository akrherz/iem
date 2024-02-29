"""Generate a plot of GDD"""

import datetime

from pyiem.util import logger, web2ldm

LOG = logger()


def main():
    """Go Main Go"""
    today = datetime.date.today()
    first = today.replace(day=1)
    url = (
        "http://iem.local/plotting/auto/plot/97/d:sector::sector:IA::"
        f"var:gdd_sum::gddbase:50::gddceil:86::"
        f"date1:{first.strftime('%Y-%m-%d')}::usdm:no::"
        f"date2:{today.strftime('%Y-%m-%d')}::p:contour::cmap:RdBu_r::c:yes"
        ".png"
    )
    pqstr = "plot c 000000000000 summary/gdd_mon.png bogus png"
    LOG.info(url)
    LOG.info(pqstr)
    res = web2ldm(url, pqstr)
    if not res:
        LOG.info("failed to work!")


if __name__ == "__main__":
    main()
