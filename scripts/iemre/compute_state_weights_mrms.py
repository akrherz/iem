"""Figure out the grid weighting for each state we care about"""
from __future__ import print_function
import os
import datetime

import netCDF4
import numpy as np
from tqdm import tqdm
from pyiem import iemre
from pyiem.util import get_dbconn

POSTGIS = get_dbconn('postgis', user='nobody')


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
    nc.createDimension('lat', (iemre.NORTH - iemre.SOUTH) * 100.0)
    nc.createDimension('lon', (iemre.EAST - iemre.WEST) * 100.0)
    nc.createDimension('nv', 2)

    lat = nc.createVariable('lat', np.float, ('lat',))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    # Grid centers
    lat[:] = np.arange(iemre.SOUTH + 0.005, iemre.NORTH, 0.01)

    lat_bnds = nc.createVariable('lat_bnds', np.float, ('lat', 'nv'))
    lat_bnds[:, 0] = np.arange(iemre.SOUTH, iemre.NORTH, 0.01)
    lat_bnds[:, 1] = np.arange(iemre.SOUTH + 0.01, iemre.NORTH + 0.01, 0.01)

    lon = nc.createVariable('lon', np.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = np.arange(iemre.WEST, iemre.EAST, 0.01)

    lon_bnds = nc.createVariable('lon_bnds', np.float, ('lon', 'nv'))
    lon_bnds[:, 0] = np.arange(iemre.WEST, iemre.EAST, 0.01)
    lon_bnds[:, 1] = np.arange(iemre.WEST + 0.01, iemre.EAST + 0.01, 0.01)

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
    mask = nc.variables['domain']
    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        mask[:] = np.where(nc.variables[state][:] > 0, 1, mask)

    nc.close()


def do_weighting(fn):
    """ Do the magic """
    pcursor = POSTGIS.cursor()
    # thr MI
    for state in ['IA', 'ND', 'SD', 'KS', 'NE', 'MO', 'IN', 'IL', 'OH', 'MI',
                  'WI', 'MN', 'KY']:
        nc = netCDF4.Dataset(fn, 'a')
        pcursor.execute("""SELECT ST_xmin(the_geom), ST_xmax(the_geom),
        ST_ymin(the_geom), ST_ymax(the_geom) from states WHERE
        state_abbr = '%s' """ % (state,))
        row = pcursor.fetchone()
        xmin = row[0] - 0.1
        xmax = row[1] + 0.1
        ymin = row[2] - 0.1
        ymax = row[3] + 0.1
        print('Processing State: %s' % (state,))
        data = np.zeros(np.shape(nc.variables[state][:]))
        for i, lon in enumerate(tqdm(nc.variables['lon'][:])):
            for j, lat in enumerate(nc.variables['lat'][:]):
                # Don't compute 0s, if we don't have to
                if lon < xmin or lon > xmax or lat < ymin or lat > ymax:
                    data[j, i] = 0.0
                    continue

                # start LL
                geom = ("MULTIPOLYGON(((%s %s, %s %s, %s %s, %s %s, %s %s"
                        ")))"
                        ) % (lon, lat,
                             lon, lat + 0.01,
                             lon + 0.01, lat + 0.01,
                             lon + 0.01, lat,
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
    fn = "/mesonet/data/iemre/state_weights_mrms.nc"
    if not os.path.isfile(fn):
        create_file(fn)
    do_weighting(fn)
    do_mask(fn)


if __name__ == '__main__':
    main()
