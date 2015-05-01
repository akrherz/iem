"""Attempt to manage the disaster that is IEM symlinking"""
import sys
import os

# LINK , TARGET
PAIRS = [
         ['/mesonet/merra', '/mnt/mtarchive/longterm/merra'],
         ['/mesonet/nawips', '/mnt/mesonet2/gempak'],
         ['/mesonet/scripts', '/mnt/mesonet2/scripts'],
         ['/mesonet/TABLES', '/mnt/mesonet2/TABLES'],
         ['/mesonet/tmp', '/mnt/mesonet2/tmp'],
         ['/mesonet/wepp', '/mnt/idep'],
         ['/mesonet/ARCHIVE/dailydata', '/mnt/mtarchive/longterm/dailydata'],
         ['/mesonet/ARCHIVE/data', '/mnt/mesonet2/ARCHIVE/data'],
         ['/mesonet/ARCHIVE/gempak', '/mnt/mtarchive/longterm/gempak'],
         ['/mesonet/ARCHIVE/nexrad', '/mnt/mtarchive/longterm/nexrad3_iowa'],
         ['/mesonet/ARCHIVE/raw', '/mnt/mesonet2/ARCHIVE/raw'],
         ['/mesonet/ARCHIVE/rer', '/mnt/mesonet/ARCHIVE/rer'],
         ['/mesonet/ARCHIVe/wunder', '/mnt/mesonet2/ARCHIVE/wunder'],
         ['/mesonet/data/alerts', '/mnt/mesonet2/data/alerts'],
         ['/mesonet/data/dm', '/mnt/mesonet2/data/dm'],
         ['/mesonet/data/dotcams', '/mnt/mesonet2/data/dotcams'],
         ['/mesonet/data/gempak', '/mnt/mesonet2/data/gempak'],
         ['/mesonet/data/harry', '/mnt/mesonet/ARCHIVE/raw/harry'],
         ['/mesonet/data/iemre', '/mnt/mesonet/data/iemre'],
         ['/mesonet/data/incoming', '/mnt/mesonet2/data/incoming'],
         ['/mesonet/data/logs', '/mnt/mesonet2/data/logs'],
         ['/mesonet/data/madis', '/mnt/mesonet2/data/madis'],
         ['/mesonet/data/model', '/mnt/mesonet2/data/model'],
         ['/mesonet/data/nccf', '/mnt/mesonet2/data/nccf'],
         ['/mesonet/data/nexrad', '/mnt/mesonet2/data/nexrad'],
         ['/mesonet/data/smos', '/mnt/mesonet2/data/smos'],
         ['/mesonet/data/text', '/mnt/mesonet2/data/text'],
         ['/mesonet/share/cases', '/mnt/mesonet/share/cases'],
         ['/mesonet/share/climodat', '/mnt/mesonet2/share/climodat'],
         ['/mesonet/share/features', '/mnt/mesonet/share/features'],
         ['/mesonet/share/frost', '/mmt/mesonet/share/frost'],
         ['/mesonet/share/iemmaps', '/mnt/mesonet/share/iemmaps'],
         ['/mesonet/share/iemre', '/mnt/mesonet/data/iemre'],
         ['/mesonet/share/lapses', '/mnt/mesonet/share/lapses'],
         ['/mesonset/share/mec', '/mnt/mesonet/share/mec'],
         ['/mesonet/share/pickup', '/mnt/mesonet2/share/pickup'],
         ['/mesonet/share/pics', '/mnt/mesonet/share/pics'],
         ['/mesonet/share/present', '/mnt/mesonet/share/present'],
         ['/mesonet/share/usage', '/mnt/mesonet/share/usage'],
         ['/mesonet/share/windrose', '/mnt/mesonet2/share/windrose'],
         ]


def do(link, target):
    """Do things"""
    if not os.path.isdir(target):
        print('ERROR: link target: %s is not found' % (target,))
        return
    if not os.path.islink(link) and os.path.isdir(link):
        print('ERROR: symlink: %s is already a directory!' % (link,))
        return
    if os.path.islink(link):
        oldtarget = os.path.realpath(link)
        if oldtarget == target:
            return
    print("%s -> %s" % (link, target))
    os.symlink(target, link)


def main(argv):
    """Go Main"""
    for (link, target) in PAIRS:
        do(link, target)


if __name__ == '__main__':
    main(sys.argv)
