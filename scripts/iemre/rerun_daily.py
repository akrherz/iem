import datetime
import subprocess
import grid_climodat

sts = datetime.datetime(1893,1,1)
ets = datetime.datetime(2013,5,30)
interval = datetime.timedelta(days=1)
now = sts
while now < ets:
    print now
    if now.day == 1 and now.month == 1:
        subprocess.call("python init_daily.py %s" % (now.year,), shell=True)
    grid_climodat.main( now )
    now += interval
