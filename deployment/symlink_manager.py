"""Attempt to manage the disaster that is IEM symlinking"""
import os
import datetime

from pyiem.util import logger

LOG = logger()

# LINK , TARGET
PAIRS = [
    ["/mesonet/data/merra2", "/mnt/mesonet2/data/merra2"],
    ["/mesonet/nawips", "/mnt/mesonet2/gempak"],
    ["/mesonet/scripts", "/mnt/mesonet2/scripts"],
    ["/mesonet/wepp", "/mnt/mesonet2/idep"],
    ["/mesonet/ARCHIVE/gempak", "/mnt/mesonet2/longterm/gempak"],
    ["/mesonet/ARCHIVE/raw", "/mnt/mesonet2/longterm/raw"],
    ["/mesonet/ARCHIVE/rer", "/mnt/mesonet/ARCHIVE/rer"],
    ["/mesonet/data/dotcams", "/mnt/mesonet2/data/dotcams"],
    ["/mesonet/data/gempak", "/mnt/mesonet2/data/gempak"],
    ["/mesonet/data/iemre", "/mnt/mesonet2/data/iemre"],
    ["/mesonet/data/prism", "/mnt/mesonet2/data/prism"],
    ["/mesonet/data/incoming", "/mnt/mesonet2/data/incoming"],
    ["/mesonet/data/madis", "/mnt/mesonet2/data/madis"],
    ["/mesonet/data/model", "/mnt/mesonet2/data/model"],
    ["/mesonet/data/ndfd", "/mnt/mesonet2/data/ndfd"],
    ["/mesonet/data/nexrad", "/data/gempak/nexrad"],
    ["/mesonet/data/smos", "/mnt/mesonet2/data/smos"],
    ["/mesonet/data/stage4", "/mnt/mesonet2/data/stage4"],
    ["/mesonet/data/text", "/mnt/mesonet2/data/text"],
    ["/mesonet/share/cases", "/mnt/mesonet/share/cases"],
    ["/mesonet/share/climodat", "/mnt/mesonet2/share/climodat"],
    ["/mesonet/share/features", "/mnt/mesonet/share/features"],
    ["/mesonet/share/frost", "/mnt/mesonet/share/frost"],
    ["/mesonet/share/iemmaps", "/mnt/mesonet/share/iemmaps"],
    ["/mesonet/share/lapses", "/mnt/mesonet/share/lapses"],
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
    for year in range(1893, 2020):
        link = "/mesonet/ARCHIVE/data/%s" % (year,)
        target = "/mnt/mtarchive3/ARCHIVE/data/%s" % (year,)
        workflow(link, target)
    for year in range(2020, datetime.date.today().year + 2):
        link = "/mesonet/ARCHIVE/data/%s" % (year,)
        target = "/mnt/archive00/ARCHIVE/data/%s" % (year,)
        workflow(link, target)

    for (link, target) in PAIRS:
        workflow(link, target)


if __name__ == "__main__":
    main()
