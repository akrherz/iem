# Look into our archive and make sure we have what we need!

import subprocess
import os
import psycopg2
import datetime
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor()

mcursor.execute("""SELECT sts, template, interval from archive_products
    WHERE id = 44""")
row = mcursor.fetchone()

tpl = row[1].replace("https://mesonet.agron.iastate.edu/archive/data/",
                     "/mesonet/ARCHIVE/data/").replace("%i", '%M')
now = row[0]
interval = datetime.timedelta(minutes=row[2])
ets = datetime.datetime.now().replace(tzinfo=now.tzinfo)

while now < ets:
    fp = now.strftime(tpl)
    if not os.path.isfile(fp):
        cmd = "python q2_5min_rate.py %s" % (now.strftime("%Y %m %d %H %M"), )
        subprocess.call(cmd, shell=True)
        print 'Missing', now
    now += interval
