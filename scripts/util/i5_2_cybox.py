"""Upload i5 analysis to CyBox"""
import os
import datetime
import glob
import logging
import sys

from pyiem.ftpsession import send2box


def main(argv):
    """Go Main!"""
    if len(argv) > 1 and argv[1] == 'debug':
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logging.debug("Setting logging to debug...")

    ceiling = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    os.chdir("/mesonet/share/pickup/ntrans")

    local_filenames = {}
    remote_filenames = {}
    for fn in glob.glob("*.zip"):
        valid = datetime.datetime.strptime(fn[3:15], '%Y%m%d%H%M')
        if valid >= ceiling:
            continue
        rp = valid.strftime("/NTRANS/wxarchive/%Y/%m/%d/%H")
        if fn.startswith("fx"):
            rp = valid.strftime("/NTRANS/wxarchive/forecast/%Y/%m")
        if rp not in remote_filenames:
            local_filenames[rp] = []
            remote_filenames[rp] = []
        # Move file to temp fn so that we don't attempt to upload this twice
        fn2 = "%s.xfer" % (fn,)
        os.rename(fn, fn2)
        local_filenames[rp].append(fn2)
        remote_filenames[rp].append(fn)

    fs = None
    for rp in remote_filenames:
        _ftps, ress = send2box(
            local_filenames[rp], rp,
            remotenames=remote_filenames[rp], fs=fs
        )
        for fn, res in zip(local_filenames[rp], ress):
            if res is not False:
                os.unlink(fn)


if __name__ == '__main__':
    main(sys.argv)
