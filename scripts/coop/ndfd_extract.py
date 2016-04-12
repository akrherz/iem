"""Extract data from gridded NDFD, seven days of data

Total precipitation
Maximum temperature
Minimum temperature

Attempt to derive climodat data from the NDFD database, we will use the 00 UTC
files.

"""
import psycopg2
import sys
import datetime
import pytz
import pyproj
import numpy as np
import pygrib
import os
from pyiem.datatypes import temperature
from pyiem.network import Table as NetworkTable

nt = NetworkTable(('IACLIMATE', 'ILCLIMATE', 'INCLIMATE', 'OHCLIMATE',
                   'MICLIMATE', 'KYCLIMATE', 'WICLIMATE', 'MNCLIMATE',
                   'SDCLIMATE', 'NDCLIMATE', 'NECLIMATE', 'KSCLIMATE',
                   'MOCLIMATE'))


def do_precip(gribs, ftime, data):
    # Precip
    try:
        sel = gribs.select(parameterName='Total precipitation')
    except:
        return
    if data['x'] is None:
        data['proj'] = pyproj.Proj(sel[0].projparams)
        llcrnrx, llcrnry = data['proj'](
            sel[0]['longitudeOfFirstGridPointInDegrees'],
            sel[0]['latitudeOfFirstGridPointInDegrees'])
        nx = sel[0]['Nx']
        ny = sel[0]['Ny']
        dx = sel[0]['DxInMetres']
        dy = sel[0]['DyInMetres']
        data['x'] = llcrnrx + dx * np.arange(nx)
        data['y'] = llcrnry + dy * np.arange(ny)
    cst = ftime - datetime.timedelta(hours=6)
    key = cst.strftime("%Y-%m-%d")
    d = data['fx'].setdefault(key, dict(precip=None, high=None, low=None))
    print("Writting precip %s from ftime: %s" % (key, ftime))
    if d['precip'] is None:
        d['precip'] = sel[0].values
    else:
        d['precip'] += sel[0].values


def do_temp(name, dkey, gribs, ftime, data):
    try:
        sel = gribs.select(parameterName=name)
    except:
        return
    cst = ftime - datetime.timedelta(hours=6)
    key = cst.strftime("%Y-%m-%d")
    d = data['fx'].setdefault(key, dict(precip=None, high=None, low=None))
    print("Writting %s %s from ftime: %s" % (name, key, ftime))
    d[dkey] = temperature(sel[0].values, 'K').value('F')


def process(ts):
    """Do Work"""
    data = {'x': None, 'y': None, 'proj': None, 'fx': dict()}
    for fhour in range(1, 200):
        ftime = ts + datetime.timedelta(hours=fhour)
        fn = ("/mesonet/ARCHIVE/data/%s/%02i/%02i/model/ndfd/%02i/"
              "ndfd.t%02iz.awp2p5f%03i.grib2"
              ) % (ts.year, ts.month, ts.day, ts.hour, ts.hour, fhour)
        if not os.path.isfile(fn):
            continue
        print("-> " + fn)
        gribs = pygrib.open(fn)
        do_precip(gribs, ftime, data)
        do_temp('Maximum temperature', 'high', gribs, ftime, data)
        do_temp('Minimum temperature', 'low', gribs, ftime, data)

    return data


def dbsave(ts, data):
    """Save the data! """
    pgconn = psycopg2.connect(database='coop', host='iemdb')
    cursor = pgconn.cursor()
    # Check to see if we already have data for this date
    cursor.execute("""SELECT id from forecast_inventory
      WHERE model = 'NDFD' and modelts = %s""", (ts,))
    if cursor.rowcount > 0:
        modelid = cursor.fetchone()[0]
        cursor.execute("""DELETE from alldata_forecast where
        modelid = %s""", (modelid,))
        if cursor.rowcount > 0:
            print("Removed %s previous entries" % (cursor.rowcount,))
    else:
        cursor.execute("""INSERT into forecast_inventory(model, modelts)
        VALUES ('NDFD', %s) RETURNING id""", (ts,))
        modelid = cursor.fetchone()[0]

    for date in data['fx'].keys():
        d = data['fx'][date]
        if (d['high'] is None or d['low'] is None or
                d['precip'] is None):
            print("Missing data for date: %s" % (date,))
            del(data['fx'][date])

    for sid in nt.sts.keys():
        # Skip virtual stations
        if sid[2:] == '0000' or sid[2] == 'C':
            continue
        x, y = data['proj'](nt.sts[sid]['lon'], nt.sts[sid]['lat'])
        i = np.digitize([x], data['x'])[0]
        j = np.digitize([y], data['y'])[0]
        for date in data['fx']:
            d = data['fx'][date]
            cursor.execute("""INSERT into alldata_forecast(modelid,
            station, day, high, low, precip)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (modelid, sid, date, float(d['high'][j, i]),
                  float(d['low'][j, i]),
                  round(float(d['precip'][j, i] / 25.4), 2)))
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go!"""
    # Extract 12 UTC Data
    ts = datetime.datetime.utcnow()
    ts = ts.replace(tzinfo=pytz.timezone("UTC"), hour=0, minute=0, second=0,
                    microsecond=0)
    data = process(ts)
    dbsave(ts, data)

if __name__ == '__main__':
    main(sys.argv)
