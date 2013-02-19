"""
Generate a windrose for each site in the ASOS network, me thinks...
"""
import network
import sys
import subprocess
net = sys.argv[1]
nt = network.Table( net )
for sid in nt.sts.keys():
    subprocess.call("python make_windrose.py %s %s" % (net, sid), shell=True)
