#!/usr/bin/env python
import sys
import cgi
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pyiem.plot import MapPlot
import base64
import cStringIO


def main(argv):
    """ Do Something Fun"""
    m = MapPlot()
    ram = cStringIO.StringIO()
    plt.savefig(ram, format='png', dpi=100)
    ram.seek(0)
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(base64.b64encode(ram.read()))

if __name__ == '__main__':
    main(sys.argv)
