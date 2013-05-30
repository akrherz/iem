import datetime
import grid_asos
import sys
import pytz

yr = int(sys.argv[1])

sts = datetime.datetime(yr,1,1)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = sts.replace(year=yr+1)
interval = datetime.timedelta(hours=1)
now = sts
while now < ets:
    print now
    grid_asos.main( now )
    now += interval
