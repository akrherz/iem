"""Attempt to manage the disaster that is IEM symlinking"""
import os

from pyiem.util import logger

LOG = logger()

# LINK , TARGET
M2 = "/mnt/mesonet2"
M7 = "/mnt/mesonet7"
PAIRS = [
    ["/mesonet/data/merra2", f"{M2}/data/merra2"],
    ["/mesonet/nawips", f"{M2}/gempak"],
    ["/mesonet/wepp", f"{M2}/idep"],
    ["/mesonet/ARCHIVE/gempak", f"{M2}/longterm/gempak"],
    ["/mesonet/ARCHIVE/raw", f"{M2}/longterm/raw"],
    ["/mesonet/ARCHIVE/rer", f"{M7}/ARCHIVE/rer"],
    ["/mesonet/data/dotcams", f"{M2}/data/dotcams"],
    ["/mesonet/data/gempak", f"{M2}/data/gempak"],
    ["/mesonet/data/iemre", f"{M2}/data/iemre"],
    ["/mesonet/data/prism", f"{M2}/data/prism"],
    ["/mesonet/data/incoming", f"{M2}/data/incoming"],
    ["/mesonet/data/madis", f"{M2}/data/madis"],
    ["/mesonet/data/model", f"{M2}/data/model"],
    ["/mesonet/data/mrms", f"{M2}/data/mrms"],
    ["/mesonet/data/ndfd", f"{M2}/data/ndfd"],
    ["/mesonet/data/smos", f"{M2}/data/smos"],
    ["/mesonet/data/stage4", f"{M2}/data/stage4"],
    ["/mesonet/data/text", f"{M2}/data/text"],
    ["/mesonet/ldmdata", f"{M2}/ldmdata"],  # May fail if node writes data
    ["/mesonet/share/cases", f"{M7}/share/cases"],
    ["/mesonet/share/climodat", f"{M2}/share/climodat"],
    ["/mesonet/share/features", f"{M7}/share/features"],
    ["/mesonet/share/frost", f"{M7}/share/frost"],
    ["/mesonet/share/iemmaps", f"{M7}/share/iemmaps"],
    ["/mesonet/share/lapses", f"{M7}/share/lapses"],
    ["/mesonet/share/pickup", f"{M2}/share/pickup"],
    ["/mesonet/share/pics", f"{M7}/share/pics"],
    ["/mesonet/share/present", f"{M7}/share/present"],
    ["/mesonet/share/usage", f"{M7}/share/usage"],
    ["/mesonet/share/windrose", f"{M7}/share/windrose"],
    ["/mesonet/home", f"{M7}/home"],
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
        path = f"/mesonet/{mysubdir}"
        if not os.path.isdir(path):
            os.makedirs(path)
    # Quasi dynamic generation of /mesonet/ARCHIVE/data/YYYY links
    if not os.path.isdir("/mesonet/ARCHIVE/data"):
        os.makedirs("/mesonet/ARCHIVE/data")
    for year in range(1893, 2019):
        link = f"/mesonet/ARCHIVE/data/{year}"
        target = f"/mnt/mtarchive2/ARCHIVE/data/{year}"
        workflow(link, target)
    for year in range(2019, 2023):
        link = f"/mesonet/ARCHIVE/data/{year}"
        target = f"/mnt/archive00/ARCHIVE/data/{year}"
        workflow(link, target)
    for year in range(2023, 2024):
        link = f"/mesonet/ARCHIVE/data/{year}"
        target = f"/mnt/mtarchive2/ARCHIVE/data/{year}"
        workflow(link, target)

    for (link, target) in PAIRS:
        workflow(link, target)


if __name__ == "__main__":
    main()
