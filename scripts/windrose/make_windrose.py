"""
Drive a windrose for a given network and site
"""
import network
import iemplot
import datetime
import sys
net = sys.argv[1]
nt = network.Table( net )
sid = sys.argv[2]

database = 'asos'
if net in ('KCCI','KELO','KIMT'):
    database = 'snet'
elif net in ('IA_RWIS'):
    database = 'rwis'
elif net in ('ISUSM'):
    database = 'isuag'


fp = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (sid,)
print "%4s %-20.20s -- YR" % (sid, nt.sts[sid]['name']),
iemplot.windrose(sid, fp=fp, database=database)
for m in range(1,13):
    fp = "/mesonet/share/windrose/climate/monthly/%02i/%s_%s.png" % (
        m, sid, datetime.datetime(2000,m,1).strftime("%b").lower() )
    print "%s" % (m,),
    iemplot.windrose(sid, fp=fp, months=(m,), database=database)

print