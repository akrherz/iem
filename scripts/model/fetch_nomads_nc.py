"""
Download netcdf data from NOMADS Thredds service, run as

/usr/local/python/bin/python fetch_nomads_nc.py
"""
import mx.DateTime
import subprocess

# start time, GMT
sts = mx.DateTime.DateTime(2010,11,1)
# end time, GMT
ets = mx.DateTime.DateTime(2012,9,17)
# Interval
interval = mx.DateTime.RelativeDateTime(hours=6)

now = sts
while now < ets:
    for F in ['000', '006', '012', '018', '024']:
        print 'Downloading', now.strftime("%Y-%m-%d %H"), ' Forecast Hr:', F
        command = now.strftime("wget -q -O '%Y%m%d%H-"+F+".nc' 'http://nomads.ncdc.noaa.gov/thredds/ncss/grid/gfs-004/%Y%m/%Y%m%d/gfs_4_%Y%m%d_%H00_"+F+".grb2?var=Geopotential_height&spatial=all&north=90.0000&west=0.0000&east=-0.5000&south=-90.0000&temporal=all&time_start=%Y-%m-%dT%H:00:00Z&time_end=%Y-%m-%dT%H:00:00Z&horizStride='")
        subprocess.call(command, shell=True)
    
    now += interval