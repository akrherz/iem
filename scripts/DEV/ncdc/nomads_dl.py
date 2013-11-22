'''
 KAMW 41.99044   -93.61852
 KCID 41.8829    -91.72459
'''

import datetime
import pytz
import urllib2

sts = datetime.datetime(2012,8,20)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = datetime.datetime(2013,11,1)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))

interval = datetime.timedelta(hours=12)

out = open('gfs_cedarrapids.csv', 'a')
#out.write("fhour,runtime,validtime,RH,TMPK,UVEL,VVEL\n")

now = sts
while now < ets:
    print now
    for hr in range(0,49,3):
        ts = now + datetime.timedelta(hours=hr)
        tstr = ts.strftime("%Y-%m-%dT%H:00:00Z")
        shr = "%03i" % (hr,)
        uri = now.strftime(('http://nomads.ncdc.noaa.gov/thredds/ncss/grid/'
            +'gfs-004/%Y%m/%Y%m%d/gfs_4_%Y%m%d_%H00_'+shr+'.grb2?'
            +'var=Relative_humidity_height_above_ground'
            +'&var=Temperature_height_above_ground'
            +'&var=U-component_of_wind_height_above_ground'
            +'&var=V-component_of_wind_height_above_ground'
            +'&latitude=41.88&longitude=-91.72&temporal=all'
            +'&time_start='+tstr+'&time_end='+tstr+'&time='+tstr+''
            +'&vertCoord=0&accept=csv&point=true'))
        try:
            data = urllib2.urlopen(uri).read()
            line = data.split('\n')[1]
            out.write("%s,%s,%s\n" % (hr, now.strftime("%Y-%m-%d %H:%M:%SZ"), 
                                      line))
        except Exception, exp:
            print exp
    
    now += interval
    
out.close()
