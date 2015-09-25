import ephem
import datetime
from pyiem import iemre
from pyiem.plot import MapPlot
import numpy as np
import netCDF4
sun = ephem.Sun()

nc = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
w = nc.variables['domain'][:]

def do(lat, lon):
    loc = ephem.Observer()
    loc.lat = `lat`
    loc.long = `lon`
    loc.date = "2013/06/21"

    rise1 = loc.next_rising(sun).datetime()
    loc.date = "2013/06/22"
    set1 = loc.next_setting(sun).datetime()
    rise2 = loc.next_rising(sun).datetime()
    loc.date = "2013/06/23"
    set2 = loc.next_setting(sun).datetime()

    day1 = (set1 - rise1).seconds + (set1 - rise1).microseconds / 1000000.0
    day2 = (set2 - rise2).seconds + (set2 - rise2).microseconds / 1000000.0
    return day1 - day2

xs,ys = np.meshgrid( np.concatenate([iemre.XAXIS, [iemre.XAXIS[-1] + 0.25,]]), 
                     np.concatenate([iemre.YAXIS, [iemre.YAXIS[-1] + 0.25,]]))

secs = np.zeros( np.shape(w) , 'f')

for i, lon in enumerate(iemre.XAXIS):
    print i, len(iemre.XAXIS)
    for j, lat in enumerate(iemre.YAXIS):
        secs[j,i] = do(lat, lon)

print np.shape(w)
print np.shape(secs)
#secs = np.where(w == 1, secs, 0)

m = MapPlot(sector='midwest', title='21 Jun to 22 Jun 2013 Decrease in Daylight Time',
            subtitle='No local topography considered')

m.contourf(iemre.XAXIS, iemre.YAXIS, secs, np.arange(2,6.1,0.25), units='seconds')

m.postprocess(filename='test.png')
