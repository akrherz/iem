"""Attempt to manage the disaster that is IEM symlinking"""
import os
import datetime

from pyiem.util import logger

LOG = logger()

# LINK , TARGET
PAIRS = [
    ["/mesonet/merra", "/mnt/mtarchive/longterm/merra"],
    ["/mesonet/merra2", "/mnt/mtarchive/longterm/merra2"],
    ["/mesonet/nawips", "/mnt/mesonet2/gempak"],
    ["/mesonet/scripts", "/mnt/mesonet2/scripts"],
    ["/mesonet/wepp", "/mnt/idep"],
    ["/mesonet/ARCHIVE/dailydata", "/mnt/mtarchive/longterm/dailydata"],
    ["/mesonet/ARCHIVE/gempak", "/mnt/mtarchive/longterm/gempak"],
    ["/mesonet/ARCHIVE/nexrad", "/mnt/mtarchive/longterm/nexrad3_iowa"],
    ["/mesonet/ARCHIVE/raw", "/mnt/mesonet2/ARCHIVE/raw"],
    ["/mesonet/ARCHIVE/rer", "/mnt/mesonet/ARCHIVE/rer"],
    ["/mesonet/data/alerts", "/mnt/mesonet2/data/alerts"],
    ["/mesonet/data/dotcams", "/mnt/mesonet2/data/dotcams"],
    ["/mesonet/data/gempak", "/mnt/mesonet2/data/gempak"],
    ["/mesonet/data/harry", "/mnt/mesonet/ARCHIVE/raw/harry"],
    ["/mesonet/data/iemre", "/mnt/mesonet2/data/iemre"],
    ["/mesonet/data/prism", "/mnt/mesonet2/data/prism"],
    ["/mesonet/data/incoming", "/mnt/mesonet2/data/incoming"],
    ["/mesonet/data/logs", "/mnt/mesonet2/data/logs"],
    ["/mesonet/data/madis", "/mnt/mesonet2/data/madis"],
    ["/mesonet/data/model", "/mnt/mesonet2/data/model"],
    ["/mesonet/data/ndfd", "/mnt/mesonet2/data/ndfd"],
    ["/mesonet/data/nexrad", "/mnt/nexrad3/nexrad"],
    ["/mesonet/data/smos", "/mnt/mesonet2/data/smos"],
    ["/mesonet/data/stage4", "/mnt/mesonet2/data/stage4"],
    ["/mesonet/data/text", "/mnt/mesonet2/data/text"],
    ["/mesonet/share/cases", "/mnt/mesonet/share/cases"],
    ["/mesonet/share/climodat", "/mnt/mesonet2/share/climodat"],
    ["/mesonet/share/features", "/mnt/mesonet/share/features"],
    ["/mesonet/share/frost", "/mnt/mesonet/share/frost"],
    ["/mesonet/share/iemmaps", "/mnt/mesonet/share/iemmaps"],
    ["/mesonet/share/iemre", "/mnt/mesonet/data/iemre"],
    ["/mesonet/share/lapses", "/mnt/mesonet/share/lapses"],
    ["/mesonet/share/mec", "/mnt/mesonet/share/mec"],
    ["/mesonet/share/pickup", "/mnt/mesonet2/share/pickup"],
    ["/mesonet/share/pics", "/mnt/mesonet/share/pics"],
    ["/mesonet/share/present", "/mnt/mesonet/share/present"],
    ["/mesonet/share/usage", "/mnt/mesonet/share/usage"],
    ["/mesonet/share/windrose", "/mnt/mesonet2/share/windrose"],
]


def workflow(link, target):
    """Do things"""
    if not os.path.isdir(target):
        LOG.info("ERROR: link target: %s is not found", target)
        return
    if not os.path.islink(link) and os.path.isdir(link):
        LOG.info("ERROR: symlink: %s is already a directory!", link)
        return
    if os.path.islink(link):
        oldtarget = os.path.realpath(link)
        if oldtarget == target:
            return
        os.unlink(link)
    LOG.info("%s -> %s", link, target)
    os.symlink(target, link)


def main():
    """Go Main"""
    # Ensure some base folders exist
    for mysubdir in ["share", "ARCHIVE", "data"]:
        path = "/mesonet/%s" % (mysubdir,)
        if not os.path.isdir(path):
            os.makedirs(path)
    # Quasi dynamic generation of /mesonet/ARCHIVE/data/YYYY links
    if not os.path.isdir("/mesonet/ARCHIVE/data"):
        os.makedirs("/mesonet/ARCHIVE/data")
    for year in range(1893, datetime.date.today().year + 1):
        link = "/mesonet/ARCHIVE/data/%s" % (year,)
        target = "/mnt/mtarchive3/ARCHIVE/data/%s" % (year,)
        workflow(link, target)

    for (link, target) in PAIRS:
        workflow(link, target)


if __name__ == "__main__":
    main()
