"""
 Download the NARR data as netcdf
 http://nomads.ncdc.noaa.gov/thredds/ncss/grid/narr/201303/20130308/narr-a_221_20130308_0000_000.grb?var=Downward_longwave_radiation_flux&var=Downward_shortwave_radiation_flux&spatial=all&north=46.4906&west=-145.5501&east=-2.2841&south=0.7269&temporal=all&time_start=2013-03-08T00%3A00%3A00Z&time_end=2013-03-08T03%3A00%3A00Z&horizStride=
"""

import datetime
import pytz
import urllib2
import subprocess
import tempfile
import os

sts = datetime.datetime(1979,1,1)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))

ets = datetime.datetime(2013,3,1)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))

interval = datetime.timedelta(hours=3)

now = sts
while now < ets:
    print now
    uri = now.strftime("http://nomads.ncdc.noaa.gov/thredds/ncss/grid/narr/"+
                       "%Y%m/%Y%m%d/narr-a_221_%Y%m%d_%H00_000.grb?"+
                       "var=Downward_longwave_radiation_flux&"+
                       "var=Downward_shortwave_radiation_flux&spatial=all"+
                       "&temporal=all")

    req = urllib2.Request(uri)
    data = urllib2.urlopen(req).read()
    
    tmpfn = tempfile.mktemp()
    o = open(tmpfn, 'w')
    o.write( data )
    o.close()

    cmd = "/home/ldm/bin/pqinsert -p 'data a %s bogus model/NARR/rad_%s.nc nc' %s" % (
                                            now.strftime("%Y%m%d%H%M"),
                                            now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(cmd, shell=True)

    os.remove(tmpfn)
    now += interval