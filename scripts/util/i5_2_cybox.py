"""Upload i5 analysis to CyBox"""
import os
from pyiem import util
import datetime
import glob
import logging
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
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
    if rp not in remote_filenames:
        local_filenames[rp] = []
        remote_filenames[rp] = []
    # Move file to temp fn so that we don't attempt to upload this twice
    fn2 = "%s.xfer" % (fn,)
    os.rename(fn, fn2)
    local_filenames[rp].append(fn2)
    remote_filenames[rp].append(fn)

for rp in remote_filenames:
    util.send2box(local_filenames[rp], rp, remotenames=remote_filenames[rp])
    for fn in local_filenames[rp]:
        os.unlink(fn)
