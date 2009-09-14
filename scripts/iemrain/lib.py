# Support library for IEMRAIN

import netCDF3, sys, os, mx.DateTime, numpy, pg, shutil

basedir = "/mesonet/share/iemrain"

def load_stations():
    """
    Load up a dictionary of station metadata that we want for Iowa
    """
    mesosite = pg.connect("mesosite", "iemdb", user="nobody")
    rs = mesosite.query("""SELECT x(geom) as lon, y(geom) as lat, id 
         from stations WHERE network in ('AWOS','IA_ASOS') and
         id != 'TVK'""").dictresult()
    meta = {}
    for i in range(len(rs)):
        meta[ rs[i]['id'] ] = rs[i]
    mesosite.close()
    return meta

def nc_lalo2pt(nc, lat, lon):
    """
    Figure out the index values for a given lat and lon
    """
    y = int( (lat - nc.variables['lat'][0]) * 100)
    x = int( (lon - nc.variables['lon'][0]) * 100)
    return x,y

def composite_lalo2pt(lat, lon):
    """
    Compute the raster x,y point for a given lat and lon
    """
    x = int(( -126.0 - lon ) / - 0.01 )
    y = int(( 50.0 - lat ) / 0.01 )
    return x, y


def load_netcdf(ts):
    """
    Return the netcdf file for this timestamp
    """
    fp = "%s/%s/%s.nc" % (basedir, ts.year, ts.strftime("%Y%m"))
    if not os.path.isfile(fp):
        print "NETCDF File %s does not exist, creating..." % (fp,)
        create_grid(ts)
        print "... done"
    return netCDF3.Dataset(fp, 'a')


def create_grid(ts):
    """
    Create the NetCDF grid file that is used for all our work
    """
    fp = "/tmp/%s.nc" % (ts.strftime("%Y%m"),)
    # Create netCDF3 object
    nc = netCDF3.Dataset(fp, 'w')
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.Conventions = "CF-1.0"
    nc.contact     = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history     = "%s Generated" % (mx.DateTime.now().strftime("%d %B %Y"),)
    nc.title       = "IEM Precipitation Analysis"

    # Setup Dimensions
    day1 = ts + mx.DateTime.RelativeDateTime(day=1,hour=0,minute=0,second=0)
    day2 = day1 + mx.DateTime.RelativeDateTime(months=1)
    tsteps = (day2-day1).days * 24 * 4
    nc.createDimension('time', tsteps)
    # Iowa Bounds -96.639706 40.375437,-90.140061 43.501196
    x0 = -96.64
    y0 =  40.37
    x1 = -90.14
    y1 =  43.50
    nc.createDimension('lat', int((y1-y0) * 100) )
    nc.createDimension('lon', int((x1-x0) * 100) )
    nc.createDimension('bnds', 2)

    # Setup Variables
    tm = nc.createVariable('time', 'd', ('time',) )
    tm.units = "minutes since %s-01 00:00:00.0" % (day1.strftime("%Y-%m"),)
    tm.calendar = "gregorian"
    tm.bounds = "time_bnds"
    tm.long_name = "time"
    tm.standard_name = "time"
    tm[:] = numpy.arange(15, (day2 - day1).minutes + 15, 15)

    tb = nc.createVariable('time_bnds', 'd', ('time','bnds') )
    val = numpy.zeros( (tsteps,2), 'd' )
    val[:,0] = numpy.arange(0, (day2 - day1).minutes , 15)
    val[:,1] = numpy.arange(15, (day2 - day1).minutes + 15, 15)
    tb[:] = val  

    lat = nc.createVariable('lat', 'd', ('lat',) )
    lat.units = "degrees_north"
    lat.long_name = "latitude"
    lat.standard_name = "latitude"
    lat[:] = numpy.arange(y0,y1 - 0.01,0.01)

    lon = nc.createVariable('lon', 'd', ('lon',) )
    lon.units = "degrees_east"
    lon.long_name = "longitude"
    lon.standard_name = "longitude"
    lon[:] = numpy.arange(x0,x1,0.01)

    precip = nc.createVariable('precipitation', 'f', ('time','lat','lon'))
    precip.units = 'kg m-2' # aka mm
    precip.standard_name = 'precipitation_flux'
    precip.long_name = 'Accumulated Precipitation'
    precip.cell_methods = 'time: sum (interval: 15 minutes)'
    #precip._FillValue = 1.e20

    nc.close()
    del nc
    newfp = "%s/%s/%s.nc" % (basedir, ts.year, ts.strftime("%Y%m"))
    shutil.move(fp, newfp)
