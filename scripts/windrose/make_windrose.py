"""
Drive a windrose for a given network and site
"""
from pyiem.network import Table as NetworkTable
from pyiem.plot import windrose
import datetime
import sys
net = sys.argv[1]
nt = NetworkTable(net)
sid = sys.argv[2]

database = 'asos'
if net in ('KCCI', 'KELO', 'KIMT'):
    database = 'snet'
elif net in ('IA_RWIS'):
    database = 'rwis'
elif net in ('ISUSM'):
    database = 'isuag'


fp = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (sid,)
print "%4s %-20.20s -- YR" % (sid, nt.sts[sid]['name']),
windrose(sid, fp=fp, database=database)
for m in range(1, 13):
    fp = ("/mesonet/share/windrose/climate/monthly/%02i/%s_%s.png"
          ) % (m, sid, datetime.datetime(2000, m, 1).strftime("%b").lower())
    print "%s" % (m,),
    windrose(sid, fp=fp, months=(m,), database=database)

print
