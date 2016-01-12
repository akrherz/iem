"""
 Script to download the NCEP stage4 data and then inject into LDM for
 sweet archival action
"""
import datetime
import pytz
import urllib2
import os
import subprocess
from pyiem.util import exponential_backoff


def download(now):
    """
    Download a given timestamp from NCEP and inject into LDM
    Example:  ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/hourly/prod/
              nam_pcpn_anal.20090916/ST4.2009091618.01h.gz
    """
    hours = [1, ]
    if now.hour % 6 == 0 and offset != 0:
        hours.append(6)
    if now.hour == 12 and offset != 0:
        hours.append(24)
    for hr in hours:
        url = "%s.%02ih.gz" % (now.strftime(("http://ftpprd.ncep.noaa.gov/"
                                             "data/nccf/com/hourly/prod/"
                                             "nam_pcpn_anal.%Y%m%d/"
                                             "ST4.%Y%m%d%H")), hr)
        data = exponential_backoff(urllib2.urlopen, url, timeout=60)
        if data is None:
            print('ncep_stage4.py: dl %s failed' % (url,))
            continue
        # Same temp file
        o = open("tmp.grib.gz", 'wb')
        o.write(data.read())
        o.close()
        subprocess.call("gunzip -f tmp.grib.gz", shell=True)
        # Inject into LDM
        cmd = ("/home/ldm/bin/pqinsert -p 'data a %s blah "
               "stage4/ST4.%s.%02ih.grib grib' tmp.grib"
               ) % (now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call(cmd, shell=True)
        os.remove('tmp.grib')

        # Do stage2 ml now
        if hr == 1:
            url = "%s.Grb.gz" % (now.strftime(("http://ftpprd.ncep.noaa.gov"
                                               "/data/nccf/com/hourly/prod/"
                                               "nam_pcpn_anal.%Y%m%d/"
                                               "ST2ml%Y%m%d%H")), )
        else:
            url = "%s.%02ih.gz" % (now.strftime(("http://ftpprd.ncep.noaa.gov/"
                                                 "data/nccf/com/hourly/prod/"
                                                 "nam_pcpn_anal.%Y%m%d/"
                                                 "ST2ml%Y%m%d%H")), hr)
        data = exponential_backoff(urllib2.urlopen, url, timeout=60)
        if data is None:
            print('ncep_stage4.py: dl %s failed' % (url,))
            continue
        # Same temp file
        o = open("tmp.grib.gz", 'wb')
        o.write(data.read())
        o.close()
        subprocess.call("gunzip -f tmp.grib.gz", shell=True)
        # Inject into LDM
        cmd = ("/home/ldm/bin/pqinsert -p 'data a %s blah "
               "stage4/ST2ml.%s.%02ih.grib grib' tmp.grib"
               ) % (now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call(cmd, shell=True)
        os.remove('tmp.grib')

if __name__ == "__main__":
    # We want this hour GMT
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.timezone("UTC"), minute=0, second=0,
                      microsecond=0)
    for offset in [33, 9, 3, 0]:
        now = utc - datetime.timedelta(hours=offset)
        download(now)
