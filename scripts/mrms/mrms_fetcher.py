"""
We need to download the data files from MRMS project

 Changes to 140.172.25.182 on 19 Sept 2014

 http://140.172.25.182/tile4/q3rad/rainrate/PRECIPRATE.20130801.095000.gz
 http://140.172.25.182/tile4/q3rad/lcref/LCREF.20130801.095000.gz
 http://140.172.25.182:/tile1/q3rad/6h_24h_acc/24HRAD.20130801.130000.gz
"""
import urllib2
import datetime
import pytz
import os

def get_uri(varname, ts, tile, iarchive):
    """ Slightly different logic to fetch archived files """
    baseuri = 'http://140.172.25.182/'
    if iarchive:
        baseuri += 'archive/%s/' % (ts.strftime("%Y/%m"))
    baseuri += 'tile%s/' % (tile,)
    if varname == 'lcref':
        baseuri += 'lcref/LCREF'
    elif varname == 'rainrate':
        baseuri += 'q3rad/rainrate/PRECIPRATE'
    elif varname == '24hrad':
        baseuri += 'q3rad/24h_acc/24HRAD'
    elif varname == '1hrad':
        baseuri += 'q3rad/1h_acc/1HRAD'
    return '%s%s' % (baseuri, ts.strftime('.%Y%m%d.%H%M00.gz'))

def fetch(ts, iarchive=False):
    """ Do the fetching for a given timestamp """
    basedir = ts.strftime("/mnt/mtarchive/data/%Y/%m/%d/mrms")
    for tile in range(1, 5):
        for varname in ['lcref', 'rainrate', '24hrad', '1hrad']:
            if varname in ['24hrad', '1hrad'] and ts.minute != 0:
                continue
            mydir = "%s/tile%s/%s" % (basedir, tile, varname)
            if not os.path.isdir(mydir):
                os.makedirs(mydir)
            uri = get_uri(varname, ts, tile, iarchive)
            fn = "%s/%s%s" % (mydir, varname, ts.strftime('.%Y%m%d.%H%M00.gz'))
            if not os.path.isfile(fn):
                try:
                    data = urllib2.urlopen(uri, timeout=10).read()
                    if data is None or len(data) == 0:
                        continue
                    fp = open(fn, 'wb')
                    fp.write(data)
                    fp.close()
                except Exception, exp:
                    if str(exp) != 'HTTP Error 404: Not Found':
                        print exp, uri
                    if os.path.isfile(fn):
                        os.unlink(fn)

def main():
    """ This is our routine """
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
    #if utcnow.minute % 2 == 0:
    #    sys.exit(0)
    utcnow -= datetime.timedelta(minutes=1)
    fetch(utcnow, False)
    for delay in [2, 4, 10, 60, 120, 1440, 2880]:
        fetch(utcnow - datetime.timedelta(minutes=delay), False)
    for delay in [60*24*3, 60*24*5]:
        fetch(utcnow - datetime.timedelta(minutes=delay), True)

if __name__ == '__main__':
    main()
