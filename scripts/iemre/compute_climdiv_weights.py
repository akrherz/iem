"""
Figure out the grid weighting for each state we care about
"""
from __future__ import print_function
import os
import datetime

import netCDF4
from pyiem import iemre
from pyiem.util import get_dbconn
import numpy
POSTGIS = get_dbconn('postgis', user='nobody')


def create_file(fn):
    """ Generate the file! """
    pcursor = POSTGIS.cursor()
    nc = netCDF4.Dataset(fn, 'w')
    nc.title = "IEM Climdiv Weighting file"
    nc.platform = "Grided Observations"
    nc.description = "IEM daily analysis on a ~25 km grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = 'CF-1.0'
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (
                    datetime.datetime.now().strftime("%d %B %Y"),)
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension('lat', iemre.NY)
    nc.createDimension('lon', iemre.NX)

    # Setup Coordinate Variables
    lat = nc.createVariable('lat', numpy.float, ('lat',))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = iemre.YAXIS

    lon = nc.createVariable('lon', numpy.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = iemre.XAXIS

    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        pcursor.execute("""
    SELECT stdiv_, xmin(ST_Extent(the_geom)), xmax(ST_Extent(the_geom)),
    ymin(ST_Extent(the_geom)), ymax(ST_Extent(the_geom)) from climate_div
    where st = %s GROUP by stdiv_
         """, (state,))
        for row in pcursor:
            stid = "%sC0%s" % (state, str(row[0])[-2:])
            st = nc.createVariable(stid, numpy.float, ('lat', 'lon'),
                                   fill_value=1.e20)
            st.units = "1"
            st.long_name = "%s weighting" % (state,)
            st.standard_name = "weighting"
            st.coordinates = "lon lat"

    nc.close()


def do_weighting(fn):
    """ Do the magic """
    pcursor = POSTGIS.cursor()
    pcursor2 = POSTGIS.cursor()
    nc = netCDF4.Dataset(fn, 'a')
    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        pcursor.execute("""
    SELECT stdiv_, xmin(ST_Extent(the_geom)), xmax(ST_Extent(the_geom)),
    ymin(ST_Extent(the_geom)), ymax(ST_Extent(the_geom)) from climate_div
    where st = %s GROUP by stdiv_
         """, (state,))
        for row in pcursor:
            lookup = row[0]
            stid = "%sC0%s" % (state, str(row[0])[-2:])
            xmin = row[1] - 0.5
            xmax = row[2] + 0.5
            ymin = row[3] - 0.5
            ymax = row[4] + 0.5
            print('Processing Climdiv: %s' % (stid,))
            data = numpy.zeros(numpy.shape(nc.variables[stid][:]))
            for i, lon in enumerate(nc.variables['lon'][:]):
                for j, lat in enumerate(nc.variables['lat'][:]):
                    # Don't compute 0s, if we don't have to
                    if lon < xmin or lon > xmax or lat < ymin or lat > ymax:
                        data[j, i] = 0.0
                        continue

                    # start LL
                    geom = ("MULTIPOLYGON(((%s %s, %s %s, %s %s, %s %s, %s %s"
                            ")))"
                            ) % (lon, lat,
                                 lon, lat + iemre.DY,
                                 lon + iemre.DX, lat + iemre.DY,
                                 lon + iemre.DX, lat,
                                 lon, lat)
                    pcursor2.execute("""
                    SELECT ST_Area(ST_Intersection(
                                ST_SetSrid(
                                ST_GeomFromText('%s'),4326), the_geom)),
                    ST_Area(ST_GeomFromText('%s'))
                    from climate_div where st = '%s' and stdiv_ = '%s'
                    """ % (geom, geom, state, lookup))
                    row = pcursor2.fetchone()
                    data[j, i] = row[0] / row[1]
            nc.variables[stid][:] = data
    nc.close()


def main():
    """Go Main Go"""
    fn = "/mesonet/data/iemre/climdiv_weights.nc"
    if not os.path.isfile(fn):
        create_file(fn)
    do_weighting(fn)


if __name__ == '__main__':
    main()
