"""
Generate some sequential load to watch what happens to IEM's backend processing
"""
import datetime
import urllib2
import random

sts = datetime.datetime(2000, 1, 1)
ets = datetime.datetime(2005, 1, 1)
interval = datetime.timedelta(minutes=5)
now = sts

cnt = 0
start = datetime.datetime.now()
istart = start
while now < ets:
    uri = now.strftime(("http://mesonet.agron.iastate.edu/"
                        "c/tile.py/1.0.0/ridge::USCOMP-N0R-"
                        "%Y%m%d%H%M/"+str(random.randint(0, 10)) +
                        "/"+str(random.randint(0, 10))+"/" +
                        str(random.randint(0, 10))+".png"))
    data = urllib2.urlopen(uri).read()
    cnt += 1
    if cnt % 100 == 0:
        delta = datetime.datetime.now() - start
        delta2 = datetime.datetime.now() - istart
        print(("%6i %9.5f req/s %9.5f req/s"
               ) % (cnt, 100.0 / delta2.total_seconds(),
                    (float(cnt) / delta.total_seconds())))
        istart = datetime.datetime.now()

    now += interval
