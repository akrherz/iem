"""Extract data from CFS

Total precipitation
Maximum temperature
Minimum temperature

Attempt to derive climodat data from the CFS, we will use the 12 UTC
files.

"""
import psycopg2
import sys
import datetime
import pytz
import logging
import numpy as np
import pygrib
import os
from pyiem.datatypes import temperature
from pyiem.network import Table as NetworkTable

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

nt = NetworkTable(('IACLIMATE', 'ILCLIMATE', 'INCLIMATE', 'OHCLIMATE',
                   'MICLIMATE', 'KYCLIMATE', 'WICLIMATE', 'MNCLIMATE',
                   'SDCLIMATE', 'NDCLIMATE', 'NECLIMATE', 'KSCLIMATE',
                   'MOCLIMATE'))


def do_agg(dkey, fname, ts, data):

    fn = ts.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/cfs/%H/" +
                      fname + ".01.%Y%m%d%H.daily.grib2"))
    if not os.path.isfile(fn):
        return
    # Precip
    gribs = pygrib.open(fn)
    for grib in gribs:
        if data['x'] is None:
            lat, lon = grib.latlons()
            data['y'] = lat[:, 0]
            data['x'] = lon[0, :]
        ftime = ts + datetime.timedelta(hours=grib.forecastTime)
        cst = ftime - datetime.timedelta(hours=6)
        key = cst.strftime("%Y-%m-%d")
        d = data['fx'].setdefault(key, dict(precip=None, high=None, low=None,
                                            srad=None))
        logger.debug("Writting %s %s from ftime: %s" % (dkey, key, ftime))
        if d[dkey] is None:
            d[dkey] = grib.values * 6 * 3600.
        else:
            d[dkey] += grib.values * 6 * 3600.


def do_temp(dkey, fname, func, ts, data):
    fn = ts.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/cfs/%H/" +
                      fname + ".01.%Y%m%d%H.daily.grib2"))
    if not os.path.isfile(fn):
        return
    gribs = pygrib.open(fn)
    for grib in gribs:
        ftime = ts + datetime.timedelta(hours=grib.forecastTime)
        cst = ftime - datetime.timedelta(hours=6)
        key = cst.strftime("%Y-%m-%d")
        if key not in data['fx']:
            continue
        d = data['fx'][key]
        logger.debug("Writting %s %s from ftime: %s" % (dkey, key, ftime))
        if d[dkey] is None:
            d[dkey] = grib.values
        else:
            d[dkey] = func(d[dkey], grib.values)


def process(ts):
    """Do Work"""
    data = {'x': None, 'y': None, 'proj': None, 'fx': dict()}
    do_agg('precip', 'prate', ts, data)
    do_temp('high', 'tmax', np.maximum, ts, data)
    do_temp('low', 'tmin', np.minimum, ts, data)
    do_agg('srad', 'dswsfc', ts, data)

    return data


def dbsave(ts, data):
    """Save the data! """
    pgconn = psycopg2.connect(database='coop', host='iemdb')
    cursor = pgconn.cursor()
    # Check to see if we already have data for this date
    cursor.execute("""SELECT id from forecast_inventory
      WHERE model = 'CFS' and modelts = %s""", (ts,))
    if cursor.rowcount > 0:
        modelid = cursor.fetchone()[0]
        cursor.execute("""DELETE from alldata_forecast where
        modelid = %s""", (modelid,))
        if cursor.rowcount > 0:
            print("Removed %s previous entries" % (cursor.rowcount,))
    else:
        cursor.execute("""INSERT into forecast_inventory(model, modelts)
        VALUES ('CFS', %s) RETURNING id""", (ts,))
        modelid = cursor.fetchone()[0]

    for date in data['fx'].keys():
        d = data['fx'][date]
        if (d['high'] is None or d['low'] is None or
                d['precip'] is None or d['srad'] is None):
            print("Missing data for date: %s" % (date,))
            del(data['fx'][date])

    for sid in nt.sts.keys():
        # Skip virtual stations
        if sid[2:] == '0000' or sid[2] == 'C':
            continue
        # Careful here, lon is 0-360 for this file
        i = np.digitize([nt.sts[sid]['lon'] + 360], data['x'])[0]
        j = np.digitize([nt.sts[sid]['lat']], data['y'])[0]
        for date in data['fx']:
            d = data['fx'][date]
            cursor.execute("""INSERT into alldata_forecast(modelid,
            station, day, high, low, precip, srad)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (modelid, sid, date,
                  temperature(d['high'][j, i], 'K').value('F'),
                  temperature(d['low'][j, i], 'K').value('F'),
                  round(float(d['precip'][j, i] / 25.4), 2),
                  d['srad'][j, i] / 1000000.))
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go!"""
    # Extract 12 UTC Data
    ts = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"), hour=12, minute=0, second=0,
                    microsecond=0)
    data = process(ts)
    dbsave(ts, data)

if __name__ == '__main__':
    main(sys.argv)
