"""
Generate a windrose for each site in the ASOS network, me thinks...
"""
import network
import sys
nt = network.Table(sys.argv[1])
for id in nt.sts.keys():
    os.system("/mesonet/python/bin/python make_windrose.py %s" % (id,))
