"""Regenerate composites to fulfill various reasons"""

from radar_composite import save
import datetime
import sys

sts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                        int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
ets = datetime.datetime(int(sys.argv[6]), int(sys.argv[7]),
                        int(sys.argv[8]), int(sys.argv[9]), int(sys.argv[10]))
interval = datetime.timedelta(minutes=5)
now = sts
while (now < ets):
    print now
    s = now.strftime("%Y%m%d%H%M")
    save('conus', 'uscomp.png', 'usrad', s, routes='a')
    save('iem', 'mwcomp.png', 'comprad', s, routes='a')
    for i in ['lot', 'ict', 'sd', 'hun']:
        save(i, '%scomp.png' % (i, ), '%srad' % (i,), s, routes='a')
    now += interval
