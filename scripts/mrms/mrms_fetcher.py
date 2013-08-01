'''
We need to download the data files from MRMS project

 http://129.15.110.182/tile4/q3rad/rainrate/PRECIPRATE.20130801.095000.gz
 http://129.15.110.182/tile4/q3rad/lcref/LCREF.20130801.095000.gz
'''
import urllib2
import datetime
import pytz
import sys
import os

def fetch(ts):
    ''' Do the fetching for a given timestamp '''
    basedir = ts.strftime("/mnt/mtarchive/data/%Y/%m/%d/mrms")
    for tile in range(1,5):
        for varname in ['lcref', 'rainrate']:
            mydir = "%s/tile%s/%s" % (basedir, tile, varname)
            if not os.path.isdir(mydir):
                os.makedirs(mydir)
            if varname == 'lcref':
                baseuri = 'http://129.15.110.182/tile'+str(tile)+'/lcref/LCREF'
            elif varname == 'rainrate':
                baseuri = 'http://129.15.110.182/tile'+str(tile)+'/q3rad/rainrate/PRECIPRATE'
            uri = "%s%s" % (baseuri, ts.strftime('.%Y%m%d.%H%M00.gz'))
            fn = "%s/%s%s" % (mydir, varname, ts.strftime('.%Y%m%d.%H%M00.gz'))
            if not os.path.isfile(fn):
                try:
                    fp = open(fn, 'wb')
                    fp.write( urllib2.urlopen(uri, timeout=10).read() )
                    fp.close()
                except Exception, exp:
                    if str(exp) != 'HTTP Error 404: Not Found':
                        print exp, uri
                    if os.path.isfile(fn):
                        os.unlink(fn)
                    
    
if __name__ == '__main__':
    ''' This is our routine '''
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
    if utcnow.minute % 2 == 0:
        sys.exit(0)
    utcnow -= datetime.timedelta(minutes=1)
    fetch( utcnow )
    for delay in [2,10,60,120,1440,2880]:
        fetch( utcnow - datetime.timedelta(minutes=delay) )