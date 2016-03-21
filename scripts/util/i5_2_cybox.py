"""Upload i5 analysis to CyBox"""
import os
from pyiem import util
import datetime
import glob

ceiling = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
os.chdir("/mesonet/share/pickup/ntrans")

remote_paths = {}
remote_names = {}
for fn in glob.glob("*.zip"):
    valid = datetime.datetime.strptime(fn[3:15], '%Y%m%d%H%M')
    if valid >= ceiling:
        continue
    rp = valid.strftime("/NTRANS/wxarchive/%Y/%m/%d/%H")
    if rp not in remote_paths:
        remote_paths[rp] = []
        remote_names[rp] = []
    # Move file to temp fn so that we don't attempt to upload this twice
    fn2 = "%s.xfer" % (fn,)
    os.rename(fn, fn2)
    remote_paths[rp].append(fn2)
    remote_names[rp].append(fn)

for rp in remote_paths:
    util.send2box(remote_paths[rp], rp, remotenames=remote_names[rp])
    for fn in remote_paths[rp]:
        os.unlink(fn)
