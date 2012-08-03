"""
Generate a windrose for each site in the ASOS network, me thinks...
"""
import network
import sys
import os
nt = network.Table(sys.argv[1])
for id in nt.sts.keys():
    os.system("python make_windrose.py %s" % (id,))
