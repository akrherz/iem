"""
Generate a map of Yearly Precipitation.

Called from climodat/run.sh
"""

import click
from pyiem.util import logger, web2ldm

LOG = logger()


@click.command()
@click.option("--year", type=int, required=True, help="Year to process")
def main(year: int):
    """Do Work."""
    url = (
        "http://iem.local/plotting/auto/plot/97/d:sector::sector:IA::"
        f"var:precip_sum::date1:{year}-01-01::usdm:no::"
        f"date2:{year}-12-31::p:contour::cmap:YlGnBu::c:yes"
        ".png"
    )
    pqstr = f"plot m 000000000000 bogus {year}/summary/total_precip.png png"
    LOG.info(url)
    LOG.info(pqstr)
    res = web2ldm(url, pqstr)
    if not res:
        LOG.warning("failed for year: %s", year)


if __name__ == "__main__":
    main()
