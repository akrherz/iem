"""Generate a plot of GDD.

Called from RUN_SUMMARY.sh
"""
import datetime

from pyiem.util import logger, web2ldm

LOG = logger()


def run(gddbase, now, fn):
    """Generate the plot"""
    url = (
        "http://iem.local/plotting/auto/plot/97/d:sector::sector:IA::"
        f"var:gdd_sum::gddbase:{gddbase}::gddceil:86::"
        f"date1:{now.strftime('%Y-05-01')}::usdm:no::"
        f"date2:{now.strftime('%Y-%m-%d')}::p:contour::cmap:RdBu_r::c:yes"
        ".png"
    )
    pqstr = f"plot c 000000000000 summary/{fn}.png bogus png"
    LOG.info(url)
    LOG.info(pqstr)
    res = web2ldm(url, pqstr)
    if not res:
        LOG.info("failed for gddbase: %s", gddbase)


def main():
    """Main()"""
    today = datetime.datetime.now()
    if today.month < 5:
        today = today.replace(year=(today.year - 1), month=11, day=1)
    run(50, today, "gdd_may1")
    run(60, today, "gdd_may1_6086")
    run(65, today, "gdd_may1_6586")


if __name__ == "__main__":
    main()
