"""Figure out the grid weighting for each state we care about"""
from __future__ import print_function
import os
import datetime

import netCDF4
import numpy as np
from pyiem import iemre
from pyiem.util import get_dbconn

POSTGIS = get_dbconn('postgis')


def create_file(fn):
    """ Generate the file! """
    nc = netCDF4.Dataset(fn, 'w')
    nc.title = "IEM State Weighting file"
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
    lat = nc.createVariable('lat', np.float, ('lat',))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = iemre.YAXIS

    lon = nc.createVariable('lon', np.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = iemre.XAXIS

    mask = nc.createVariable('domain', np.float, ('lat', 'lon'),
                             fill_value=1.e20)
    mask.units = "1"
    mask.long_name = "domain weighting"
    mask.standard_name = "weighting"
    mask.coordinates = "lon lat"

    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        st = nc.createVariable(state, np.float, ('lat', 'lon'),
                               fill_value=1.e20)
        st.units = "1"
        st.long_name = "%s weighting" % (state,)
        st.standard_name = "weighting"
        st.coordinates = "lon lat"

    nc.close()


def do_mask(fn):
    """ Use the state masks to compute the overall mask """
    nc = netCDF4.Dataset(fn, 'a')
    mask = np.zeros(nc.variables['domain'][:].shape)
    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        mask = np.where(nc.variables[state][:] > 0, 1, mask)
    nc.variables['domain'][:] = mask
    nc.close()


def do_weighting(fn):
    """ Do the magic """
    pcursor = POSTGIS.cursor()
    nc = netCDF4.Dataset(fn, 'a')
    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        pcursor.execute("""SELECT ST_xmin(the_geom), ST_xmax(the_geom),
        ST_ymin(the_geom), ST_ymax(the_geom) from states WHERE
        state_abbr = '%s' """ % (state,))
        row = pcursor.fetchone()
        xmin = row[0] - 0.5
        xmax = row[1] + 0.5
        ymin = row[2] - 0.5
        ymax = row[3] + 0.5
        print('Processing State: %s' % (state,))
        data = np.zeros(nc.variables[state][:].shape)
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
                pcursor.execute("""
    SELECT ST_Area(ST_Intersection(ST_SetSrid(ST_GeomFromText('%s'),4326),
    the_geom)),
    ST_Area(ST_GeomFromText('%s'))
    from states where state_abbr = '%s'
                """ % (geom, geom, state))
                row = pcursor.fetchone()
                data[j, i] = row[0] / row[1]
        nc.variables[state][:] = data
    nc.close()


def main():
    """Go Main"""
    fn = "/mesonet/data/iemre/state_weights.nc"
    if not os.path.isfile(fn):
        create_file(fn)
    do_weighting(fn)
    do_mask(fn)


if __name__ == '__main__':
    main()
