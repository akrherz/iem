"""Upload i5 analysis to CyBox"""
import os
from pyiem import util
import datetime
import glob

ceiling = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
os.chdir("/mesonet/share/pickup/ntrans")

remote_paths = {}
for fn in glob.glob("*.zip"):
    valid = datetime.datetime.strptime(fn[3:15], '%Y%m%d%H%M')
    if valid >= ceiling:
        continue
    rp = valid.strftime("/NTRANS/wxarchive/%Y/%m/%d/%H")
    if rp not in remote_paths:
        remote_paths[rp] = []
    remote_paths[rp].append(fn)

for rp in remote_paths:
    util.send2box(remote_paths[rp], rp)
    for fn in remote_paths[rp]:
        os.unlink(fn)
