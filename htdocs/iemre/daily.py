#!/usr/bin/env python
""" JSON service providing IEMRE data for a given point """

import sys
import os
import cgi
import datetime
import json

import netCDF4
import numpy as np
from pyiem import iemre, datatypes


def myrounder(val, precision):
    """round a float or give back None"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return round(val, precision)


def main():
    """Do Something Fun!"""
    form = cgi.FormContent()
    ts = datetime.datetime.strptime(form["date"][0], "%Y-%m-%d")
    lat = float(form["lat"][0])
    lon = float(form["lon"][0])
    fmt = form["format"][0]
    if fmt != 'json':
        sys.stdout.write("Content-type: text/plain\n\n")
        sys.stdout.write("ERROR: Service only emits json at this time")
        return

    i, j = iemre.find_ij(lon, lat)
    offset = iemre.daily_offset(ts)

    res = {'data': [], }

    fn = "/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year,)

    sys.stdout.write('Content-type: application/json\n\n')
    if not os.path.isfile(fn):
        sys.stdout.write(json.dumps(res))
        sys.exit()

    if i is None or j is None:
        sys.stdout.write(json.dumps({'error': 'Coordinates outside of domain'}
                                    ))
        return

    nc = netCDF4.Dataset(fn, 'r')

    c2000 = ts.replace(year=2000)
    coffset = iemre.daily_offset(c2000)

    cnc = netCDF4.Dataset("/mesonet/data/iemre/mw_dailyc.nc", 'r')

    res['data'].append({
        'daily_high_f': myrounder(
           datatypes.temperature(
                nc.variables['high_tmpk'][offset, j, i], 'K').value('F'), 1),
        '12z_high_f': myrounder(
           datatypes.temperature(
                nc.variables['high_tmpk_12z'][offset, j, i],
                'K').value('F'), 1),
        'climate_daily_high_f': myrounder(
           datatypes.temperature(
                cnc.variables['high_tmpk'][coffset, j, i], 'K').value("F"), 1),
        'daily_low_f': myrounder(
           datatypes.temperature(
                nc.variables['low_tmpk'][offset, j, i], 'K').value("F"), 1),
        '12z_low_f': myrounder(
           datatypes.temperature(
                nc.variables['low_tmpk_12z'][offset, j, i],
                'K').value('F'), 1),
        'avg_dewpoint_f': myrounder(
           datatypes.temperature(
                nc.variables['avg_dwpk'][offset, j, i], 'K').value('F'), 1),
        'climate_daily_low_f': myrounder(
           datatypes.temperature(
                cnc.variables['low_tmpk'][coffset, j, i], 'K').value("F"), 1),
        'daily_precip_in': myrounder(
           nc.variables['p01d'][offset, j, i] / 25.4, 2),
        '12z_precip_in': myrounder(
           nc.variables['p01d_12z'][offset, j, i] / 25.4, 2),
        'climate_daily_precip_in': myrounder(
           cnc.variables['p01d'][coffset, j, i] / 25.4, 2),
        'srad_mj': myrounder(
           nc.variables['rsds'][offset, j, i] * 86400. / 1000000., 2),
        'avg_windspeed_mps': myrounder(
           nc.variables['wind_speed'][offset, j, i], 2),
      })
    nc.close()
    cnc.close()

    sys.stdout.write(json.dumps(res))


if __name__ == '__main__':
    main()
