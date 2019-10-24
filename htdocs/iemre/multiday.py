#!/usr/bin/env python
"""Provide multiday values for IEMRE and friends"""
import sys
import cgi
import datetime
import json
import warnings

import numpy as np
from pyiem import iemre, datatypes
from pyiem.util import ncopen, ssw
import pyiem.prism as prismutil

warnings.simplefilter("ignore", UserWarning)
json.encoder.FLOAT_REPR = lambda o: format(o, '.2f')
json.encoder.c_make_encoder = None


def clean(val):
    """My filter"""
    if val is None or np.isnan(val) or np.ma.is_masked(val):
        return None
    return float(val)


def send_error(msg):
    """ Send an error when something bad happens(tm)"""
    ssw('Content-type: application/json\n\n')
    ssw(json.dumps({'error': msg}))
    sys.exit()


def main():
    """Go Main Go"""
    form = cgi.FieldStorage()
    ts1 = datetime.datetime.strptime(form.getfirst("date1"), "%Y-%m-%d")
    ts2 = datetime.datetime.strptime(form.getfirst("date2"), "%Y-%m-%d")
    if ts1 > ts2:
        send_error("date1 larger than date2")
    if ts1.year != ts2.year:
        send_error("multi-year query not supported yet...")
    # Make sure we aren't in the future
    tsend = datetime.date.today()
    if ts2.date() > tsend:
        ts2 = datetime.datetime.now() - datetime.timedelta(days=1)

    lat = float(form.getfirst("lat"))
    lon = float(form.getfirst("lon"))
    if lon < iemre.WEST or lon > iemre.EAST:
        send_error("lon value outside of bounds: %s to %s" % (iemre.WEST,
                                                              iemre.EAST))
    if lat < iemre.SOUTH or lat > iemre.NORTH:
        send_error("lat value outside of bounds: %s to %s" % (iemre.SOUTH,
                                                              iemre.NORTH))
    # fmt = form["format"][0]

    i, j = iemre.find_ij(lon, lat)
    offset1 = iemre.daily_offset(ts1)
    offset2 = iemre.daily_offset(ts2) + 1

    # Get our netCDF vars
    with ncopen(iemre.get_daily_ncname(ts1.year)) as nc:
        hightemp = datatypes.temperature(
            nc.variables['high_tmpk'][offset1:offset2, j, i], 'K').value("F")
        high12temp = datatypes.temperature(
            nc.variables['high_tmpk_12z'][offset1:offset2, j, i],
            'K'
        ).value("F")
        lowtemp = datatypes.temperature(
            nc.variables['low_tmpk'][offset1:offset2, j, i], 'K').value("F")
        low12temp = datatypes.temperature(
            nc.variables['low_tmpk_12z'][offset1:offset2, j, i],
            'K'
        ).value("F")
        precip = nc.variables['p01d'][offset1:offset2, j, i] / 25.4
        precip12 = nc.variables['p01d_12z'][offset1:offset2, j, i] / 25.4

    # Get our climatology vars
    c2000 = ts1.replace(year=2000)
    coffset1 = iemre.daily_offset(c2000)
    c2000 = ts2.replace(year=2000)
    coffset2 = iemre.daily_offset(c2000) + 1
    with ncopen(iemre.get_dailyc_ncname()) as cnc:
        chigh = datatypes.temperature(
            cnc.variables['high_tmpk'][coffset1:coffset2, j, i],
            'K').value("F")
        clow = datatypes.temperature(
            cnc.variables['low_tmpk'][coffset1:coffset2, j, i],
            'K').value("F")
        cprecip = cnc.variables['p01d'][coffset1:coffset2, j, i] / 25.4

    if ts1.year > 1980:
        i2, j2 = prismutil.find_ij(lon, lat)
        with ncopen("/mesonet/data/prism/%s_daily.nc" % (ts1.year, )) as nc:
            prism_precip = nc.variables['ppt'][offset1:offset2, j2, i2] / 25.4
    else:
        prism_precip = [None]*(offset2-offset1)

    if ts1.year > 2010:
        j2 = int((lat - iemre.SOUTH) * 100.0)
        i2 = int((lon - iemre.WEST) * 100.0)
        with ncopen(iemre.get_daily_mrms_ncname(ts1.year)) as nc:
            mrms_precip = nc.variables['p01d'][offset1:offset2, j2, i2] / 25.4
    else:
        mrms_precip = [None]*(offset2-offset1)

    res = {'data': [], }

    for i in range(0, offset2 - offset1):
        now = ts1 + datetime.timedelta(days=i)
        res['data'].append({'date': now.strftime("%Y-%m-%d"),
                            'mrms_precip_in': clean(mrms_precip[i]),
                            'prism_precip_in': clean(prism_precip[i]),
                            'daily_high_f': clean(hightemp[i]),
                            '12z_high_f': clean(high12temp[i]),
                            'climate_daily_high_f': clean(chigh[i]),
                            'daily_low_f': clean(lowtemp[i]),
                            '12z_low_f': clean(low12temp[i]),
                            'climate_daily_low_f': clean(clow[i]),
                            'daily_precip_in': clean(precip[i]),
                            '12z_precip_in': clean(precip12[i]),
                            'climate_daily_precip_in': clean(cprecip[i])
                            })

    ssw('Content-type: application/json\n\n')
    ssw(json.dumps(res))


if __name__ == '__main__':
    main()
