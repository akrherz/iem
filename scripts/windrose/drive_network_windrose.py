"""
Generate a windrose for each site in the ASOS network, me thinks...
"""
import network
import iemplot
import datetime
import sys
nt = network.Table(sys.argv[1])
for id in nt.sts.keys():
    fp = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (id,)
    print "All Year %s" % (id,)
    iemplot.windrose(id, fp=fp)
    for m in range(1,13):
        fp = "/mesonet/share/windrose/climate/monthly/%02i/%s_%s.png" % (
            m, id, datetime.datetime(2000,m,1).strftime("%b").lower() )
        print "Month %s %s" % (m, id)
        iemplot.windrose(id, fp=fp, months=(m,))
