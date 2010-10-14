# Look into our archive and make sure we have what we need!

import os
import iemdb
import datetime
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

mcursor.execute("""SELECT sts, template, interval from archive_products
    WHERE id = 44""")
row = mcursor.fetchone()

tpl = row[1].replace("http://mesonet.agron.iastate.edu/archive/data/", 
                     "/mnt/a1/ARCHIVE/data/").replace("%i",'%M')
now = row[0]
interval = datetime.timedelta(minutes=row[2])
ets = datetime.datetime.now().replace(tzinfo= now.tzinfo)

while now < ets:
    fp = now.strftime(tpl)
    if not os.path.isfile(fp):
        cmd = "/mesonet/python/bin/python q2_5min_rate.py %s" % (
                now.strftime("%Y %m %d %H %M"))
        os.system( cmd )
        print 'Missing', now
    now += interval