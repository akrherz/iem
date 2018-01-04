"""Process the US Climate Reference Network"""
from __future__ import print_function
import datetime
import os
import glob
import subprocess

import pytz
import pandas as pd
import requests
from metpy.units import units
from pyiem.observation import Observation
from pyiem.util import get_dbconn

BASE = "/mesonet/tmp/uscrn"
URI = "https://www1.ncdc.noaa.gov/pub/data/uscrn/products/subhourly01"
FTP = "ftp://ftp.ncdc.noaa.gov/pub/data/uscrn/products/subhourly01"


def init_year(year):
    """We need to do great things, for a great new year"""
    # We need FTP first, since that does proper wild card expansion
    subprocess.call("""
        wget '%s/%s/*.txt'
    """ % (FTP, year), shell=True)


def process_file(icursor, ocursor, filename, size):
    """Ingest these files, please
   1    WBANNO                         XXXXX
   2    UTC_DATE                       YYYYMMDD
   3    UTC_TIME                       HHmm
   4    LST_DATE                       YYYYMMDD
   5    LST_TIME                       HHmm
   6    CRX_VN                         XXXXXX
   7    LONGITUDE                      Decimal_degrees
   8    LATITUDE                       Decimal_degrees
   9    AIR_TEMPERATURE                Celsius
   10   PRECIPITATION                  mm
   11   SOLAR_RADIATION                W/m^2
   12   SR_FLAG                        X
   13   SURFACE_TEMPERATURE            Celsius
   14   ST_TYPE                        X
   15   ST_FLAG                        X
   16   RELATIVE_HUMIDITY              %
   17   RH_FLAG                        X
   18   SOIL_MOISTURE_5                m^3/m^3
   19   SOIL_TEMPERATURE_5             Celsius
   20   WETNESS                        Ohms
   21   WET_FLAG                       X
   22   WIND_1_5                       m/s
   23   WIND_FLAG                      X
    """
    fp = open(filename, 'rb')
    fp.seek(os.stat(filename).st_size - size)
    df = pd.read_csv(fp, sep=r"\s+",
                     names=['WBANNO', 'UTC_DATE', 'UTC_TIME', 'LST_DATE',
                            'LST_TIME', 'CRX_VN', 'LON', 'LAT', 'TMPC',
                            'PRECIP_MM', 'SRAD', 'SR_FLAG', 'SKINC',
                            'ST_TYPE', 'ST_FLAG', 'RH', 'RH_FLAG', 'VSM5',
                            'SOILC5', 'WETNESS', 'WET_FLAG', 'SMPS',
                            'SMPS_FLAG'],
                     converters={'WBANNO': str})
    for _, row in df.iterrows():
        valid = datetime.datetime.strptime("%s %s" % (row['UTC_DATE'],
                                                      row['UTC_TIME']),
                                           '%Y%m%d %H%M')
        print(valid)
        valid = valid.replace(tzinfo=pytz.utc)
        ob = Observation(str(row['WBANNO']), 'USCRN', valid)
        ob.data['tmpf'] = (float(row["TMPC"]) * units.degC
                           ).to(units.degF).magnitude
        ob.data['srad'] = row['SRAD']
        ob.data['tsf0'] = (float(row["SKINC"]) * units.degC
                           ).to(units.degF).magnitude
        ob.data['relh'] = row['RH']
        ob.data['c1smv'] = row['VSM5']
        ob.data['c1tmpf'] = (float(row["SOILC5"]) * units.degC
                             ).to(units.degF).magnitude
        ob.data['sknt'] = (float(row['SMPS']) * units('m/s')
                           ).to(units('miles per hour')).magnitude
        ob.save(icursor)
        table = "uscrn_t%s" % (valid.year, )
        ocursor.execute("""
        DELETE from """ + table + """ WHERE station = %s and valid = %s
        """, (row['WBANNO'], valid))
        ocursor.execute("""
        INSERT into """+table+""" (station, valid, tmpc, precip_mm, srad,
        srad_flag, skinc, skinc_flag, skinc_type, rh, rh_flag, vsm5,
        soilc5, wetness, wetness_flag, wind_mps, wind_mps_flag) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (str(row['WBANNO']), valid, row['TMPC'], row['PRECIP_MM'],
              row['SRAD'], row['SR_FLAG'], row['SKINC'], row['ST_TYPE'],
              row['ST_FLAG'], row['RH'], row['RH_FLAG'], row['VSM5'],
              row['SOILC5'], row['WETNESS'], row['WET_FLAG'], row['SMPS'],
              row['SMPS_FLAG']))


def download(year):
    """Go Great Things"""
    dirname = "%s/%s" % (BASE, year)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    os.chdir(dirname)
    files = glob.glob("*.txt")
    if not files:
        init_year(year)
        files = glob.glob("*.txt")
    queue = []
    for filename in files:
        size = os.stat(filename).st_size
        req = requests.get("%s/%s/%s" % (URI, year, filename),
                           headers={'Range':
                                    'bytes=%s-%s' % (size, size + 16000000)},
                           timeout=30)
        # No new data
        if req.status_code == 416:
            continue
        if req.status_code < 400:
            fp = open(filename, 'a')
            fp.write(req.content)
            fp.close()
            queue.append([filename, len(req.content)])
        else:
            print("Got status code %s %s" % (req.status_code, req.content))

    return queue


def main():
    """Go Main Go"""
    year = datetime.datetime.utcnow().year
    iem_pgconn = get_dbconn('iem')
    other_pgconn = get_dbconn('other')
    for [fn, size] in download(year):
        icursor = iem_pgconn.cursor()
        ocursor = other_pgconn.cursor()
        try:
            process_file(icursor, ocursor, fn, size)
        except Exception as exp:
            print("uscrn_ingest %s traceback: %s" % (fn, exp))
        icursor.close()
        ocursor.close()
        iem_pgconn.commit()
        other_pgconn.commit()


if __name__ == '__main__':
    main()
