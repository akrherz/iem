"""
Download netcdf data from NOMADS Thredds service, run as

python fetch_nomads_nc.py

http://nomads.ncdc.noaa.gov/thredds/ncss/grid/nam218/201401/20140125/nam_218_20140125_0000_000.grb?var=Pressure_reduced_to_MSL&spatial=all&north=57.3696&west=-153.0303&east=-49.2722&south=12.1133&temporal=all&time_start=2014-01-25T00%3A00%3A00Z&time_end=2014-01-25T00%3A00%3A00Z&horizStride=&addLatLon=true

"""
import mx.DateTime
import subprocess

# start time, GMT
sts = mx.DateTime.DateTime(2014,1,6)
# end time, GMT
ets = mx.DateTime.DateTime(2014,2,10)
# Interval
interval = mx.DateTime.RelativeDateTime(hours=6)

now = sts
while now < ets:
    for F in ['000']:
        print 'Downloading', now.strftime("%Y-%m-%d %H"), ' Forecast Hr:', F
        command = now.strftime("wget -q -O '%Y%m%d%H-"+F+".nc' 'http://nomads.ncdc.noaa.gov/thredds/ncss/grid/nam218/%Y%m/%Y%m%d/nam_218_%Y%m%d_%H00_"+F+".grb?var=Pressure_reduced_to_MSL&spatial=all&north=90.0000&west=0.0000&east=-0.5000&south=-90.0000&temporal=all&time_start=%Y-%m-%dT%H:00:00Z&time_end=%Y-%m-%dT%H:00:00Z&horizStride=&addLatLon=true'")
        subprocess.call(command, shell=True)
    
    now += interval
