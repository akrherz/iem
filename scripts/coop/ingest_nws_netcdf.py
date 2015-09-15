"""Ingest the NWS provided netcdf file of COOP data"""
import netCDF4
import psycopg2
import sys
import numpy as np
COOP = psycopg2.connect(database='coop', host='iemdb')
ccursor = COOP.cursor()

fn = sys.argv[1]
nc = netCDF4.Dataset(fn)
out = open('%s.csv' % (fn, ), 'w')

byear = nc.variables['byear'][:]
maxt = nc.variables['maxt'][:]
mint = nc.variables['mint'][:]
pcpn = nc.variables['pcpn'][:]
snow = nc.variables['snow'][:]
snwg = nc.variables['snwg'][:]


def convert(val, precision):
    if val < 0:
        return 'T'
    if np.ma.is_masked(val) or np.isnan(val):
        return 'M'
    return round(val, precision)

for yr in range(byear, 2016):
    for mo in range(12):
        for dy in range(31):
            high = maxt[yr-byear, mo, dy]
            if (np.ma.is_masked(high) or np.isnan(high) or
                    high < -100 or high > 150):
                high = 'M'

            low = mint[yr-byear, mo, dy]
            if (np.ma.is_masked(low) or np.isnan(low) or
                    low < -100 or low > 150):
                low = 'M'

            precip = convert(pcpn[yr-byear, mo, dy], 2)
            snowfall = convert(snow[yr-byear, mo, dy], 1)
            snowd = convert(snwg[yr-byear, mo, dy], 1)

            out.write(",".join([str(s) for s in [yr, mo+1, dy+1, high, low,
                                                 precip,
                                                 snowfall, snowd]]) + "\n")

            # sql = """INSERT into alldata_tmp(station, day, high, low, precip,
            # snow, sday, year, month, snowd) VALUES ('IA8706', '%s-%s-%s',
            # %s, %s, %s, %s, '%02i%02i', %s, %s, %s)""" % (yr,
            # mo+1, dy+1, high, low, precip, snowfall, mo+1, dy+1, yr, mo+1,
            # snowd)
            # ccursor.execute(sql)

out.close()
nc.close()
ccursor.close()
COOP.commit()
