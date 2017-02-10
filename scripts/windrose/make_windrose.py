"""
Drive a windrose for a given network and site
"""
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from pyiem.network import Table as NetworkTable
from pyiem.windrose_utils import windrose
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
elif net.find('_DCP') > 0:
    database = 'hads'


fn = "/mesonet/share/windrose/climate/yearly/%s_yearly.png" % (sid,)
print "%4s %-20.20s -- YR" % (sid, nt.sts[sid]['name']),
res = windrose(sid, database=database, sname=nt.sts[sid]['name'])
res.savefig(fn)
plt.close()
for m in range(1, 13):
    fn = ("/mesonet/share/windrose/climate/monthly/%02i/%s_%s.png"
          ) % (m, sid, datetime.datetime(2000, m, 1).strftime("%b").lower())
    print "%s" % (m,),
    res = windrose(sid, months=(m,), database=database,
                   sname=nt.sts[sid]['name'])
    res.savefig(fn)
    plt.close()

print
