"""Generate a windrose for each site in the ASOS network, me thinks...
"""
from pyiem.network import Table as NetworkTable
import sys
import subprocess
net = sys.argv[1]
nt = NetworkTable(net)
for sid in nt.sts.keys():
    subprocess.call("python make_windrose.py %s %s" % (net, sid), shell=True)
