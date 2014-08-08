""" Backfill NEXRAD files so that each USCOMP has a matching AK, HI, PR file"""

import datetime
import os
import shutil

sts = datetime.datetime(2010, 10, 25, 10, 35)
ets = datetime.datetime(2014, 8, 8, 18, 0)

now = sts
interval = datetime.timedelta(minutes=5)

while now < ets:
    if now.minute == 0 and now.hour == 0:
        print now
    for sector in ['us', 'ak', 'pr', 'hi']:
        fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"+sector+"comp/n0q_%Y%m%d%H%M.png")
        if not os.path.isfile(fn):
            mydir = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/"+sector+"comp/")
            if not os.path.isdir(mydir):
                os.makedirs(mydir)
            if sector == 'us':
                print 'Missing', fn
            shutil.copyfile('res/blank.wld', fn[:-3]+"wld")
            shutil.copyfile('res/blank.png', fn)
    now += interval