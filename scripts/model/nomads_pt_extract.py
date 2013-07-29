import datetime
import urllib2

output = open('dsm.txt', 'a')

for yr in range(1979,2013):
    sts = datetime.datetime(yr,1,1)
    ets = datetime.datetime(yr,2,1)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        print now
        uri = now.strftime("http://nomads.ncdc.noaa.gov/thredds/ncss/grid/narr-a/%Y%m/%Y%m%d/narr-a_221_%Y%m%d_%H00_000.grb?var=u_wind&var=v_wind&latitude=41.53&longitude=-93.65&temporal=all&time=%Y-%m-%dT%H%%3A00%3A00Z&vertCoord=200&accept=csv&point=true")
        try:
            data = urllib2.urlopen(uri).read()
            tokens = data.split("\n")
            output.write(tokens[1]+"\n")
        except Exception, exp:
            print exp

        now += interval

output.close()
