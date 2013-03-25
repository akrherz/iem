"""
 Script to download the NCEP stage4 data and then inject into LDM for
 sweet archival action
"""
import datetime
import pytz
import urllib2
import os
import subprocess

def download( now ):
    """
    Download a given timestamp from NCEP and inject into LDM
    Example:  ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/hourly/prod/
              nam_pcpn_anal.20090916/ST4.2009091618.01h.Z
    """
    hours = [1,]
    if now.hour % 6 == 0:
        hours.append( 6 )
    if now.hour == 12 and offset != 0:
        hours.append( 24 )
    for hr in hours:
        url = "%s.%02ih.Z" % ( now.strftime("ftp://ftpprd.ncep.noaa.gov/"+
                                "pub/data/nccf/com/hourly/prod/"+
                                "nam_pcpn_anal.%Y%m%d/ST4.%Y%m%d%H"), hr)
        try:
            data = urllib2.urlopen( url ).read()
        except IOError:
            if hr < 6:
                print "Download NCEP stage IV failure HR: %s TIME: %s" % (hr, 
                                                                          now)
            continue
        # Same temp file
        o = open("tmp.grib.Z", 'wb')
        o.write( data )
        o.close()
        os.system("gunzip -f tmp.grib.Z")
        # Inject into LDM
        cmd = "/home/ldm/bin/pqinsert -p 'data a %s blah stage4/ST4.%s.%02ih.grib grib' tmp.grib" % (
                    now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H"), hr)
        subprocess.call( cmd, shell=True )
        os.remove('tmp.grib')

if __name__ == "__main__":
    # We want this hour GMT
    utc = datetime.datetime.utcnow()
    utc = utc.replace(tzinfo=pytz.timezone("UTC"), minute=0, second=0,
                      microsecond=0)
    for offset in [33,9,3,0]:
        now = utc - datetime.timedelta(hours=offset)
        download( now )
