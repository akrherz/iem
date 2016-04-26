"""Dump baseline file as CSV, with GDD computed"""
from pyiem.datatypes import temperature, distance
import pyiem.meteorology as met
import glob
import os
import datetime

os.chdir('baseline')
for fn in glob.glob("*.met"):
    location = fn[:-4]
    o = open("%s.csv" % (location,), 'w')
    o.write("date,high[F],low[F],precip[inch],gdd[F]\n")
    for line in open(fn):
        line = line.strip()
        if not line.startswith('2012') and not line.startswith('2015'):
            continue
        tokens = line.split()
        valid = (datetime.date(int(tokens[0]), 1, 1) +
                 datetime.timedelta(days=int(tokens[1])-1))
        high = temperature(float(tokens[3]), 'C')
        low = temperature(float(tokens[4]), 'C')
        gdd = met.gdd(high, low, 50, 86)
        precip = distance(float(tokens[5]), 'MM')
        o.write(("%s,%.1f,%.1f,%.2f,%.1f\n"
                 ) % (valid.strftime("%Y-%m-%d"), high.value("F"),
                      low.value("F"), precip.value("IN"), gdd))
    o.close()
