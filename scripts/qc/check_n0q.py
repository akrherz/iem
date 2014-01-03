"""
Check the availability of NEXRAD Composites
"""
import datetime
import os
import pytz

def run(sts, ets):
    ''' Loop over a start to end time and look for missing N0Q products '''

    now = sts
    interval = datetime.timedelta(minutes=5)
    while now < ets:
        fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"
                           +"uscomp/n0q_%Y%m%d%H%M.png"))
        if not os.path.isfile(fn):
            print 'check_n0q.py %s is missing' % (fn.split("/")[-1],)
        else:
            if os.stat(fn)[6] < 600000:
                print 'check_n0q.py %s too small, size: %s' % (
                                                            fn.split("/")[-1], 
                                                            os.stat(fn)[6])
        now += interval

if __name__ == '__main__':
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.timezone("UTC"))
    sts = utc - datetime.timedelta(hours=24)
    sts = sts.replace(hour=0,minute=0,second=0,microsecond=0)
    ets = sts + datetime.timedelta(hours=24)
    run(sts, ets)