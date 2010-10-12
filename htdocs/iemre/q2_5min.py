#!/mesonet/python/bin/python
# Extract the 5 minute interval data from the Q2 netCDF files

import cgi
import os
import netCDF3
import mx.DateTime

form = cgi.FormContent()
sts = mx.DateTime.strptime( form["date"][0], "%Y-%m-%d")
sts += mx.DateTime.RelativeDateTime(minutes=5)
ets = sts + mx.DateTime.RelativeDateTime(days=1)
interval = mx.DateTime.RelativeDateTime(minutes=5)
# -110 , 55
lat = float( form["lat"][0] )
lon = float( form["lon"][0] )
x = int( (lon - -110.) / 0.01 )
y = int( (55. - lat )/ 0.01 ) 
format = form["format"][0]

def make_fp(ts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile2/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        ts.gmtime().strftime("%Y/%m/%d"), 
        ts.gmtime().strftime("%Y%m%d-%H%M") )


# Begin output
print 'Content-type: text/plain\n'
print 'DATE,TIME,PRECIP_IN'

now = sts
while now <= ets:
    # Open NETCDF File
    fp = make_fp(now)
    if not os.path.isfile(fp):
        val = "M"
    else:
        nc = netCDF3.Dataset(fp)
        val = "%.3f" % (nc.variables["preciprate_hsr"][y,x] / 12.0 / 25.4,)
        nc.close()
    # Lat, Lon
    print "%s,%s,%s" % (now.strftime("%Y-%m-%d"),
                          now.strftime("%H:%M"),
                          val)
    
    now += interval