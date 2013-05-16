import netCDF4
import iemdb
import numpy
COOP = iemdb.connect('coop')
ccursor = COOP.cursor()

nc = netCDF4.Dataset('ALO.nc')

byear = nc.variables['byear'][:]
maxt = nc.variables['maxt'][:]
mint = nc.variables['mint'][:]
pcpn = nc.variables['pcpn'][:]
snow = nc.variables['snow'][:]
snwg = nc.variables['snwg'][:]

for yr in range(byear, 2011):
  print yr
  for mo in range(12):
    for dy in range(31):
      high = float(maxt[yr-byear,mo,dy])
      if high < -100 or high > 150 or numpy.isnan(high):
        high = 'null'
      low = float(mint[yr-byear,mo,dy])
      if low < -100 or low > 150 or numpy.isnan(low):
        low = 'null'
      precip = float(pcpn[yr-byear,mo,dy])
      if precip < 0 or precip > 150 or numpy.isnan(precip):
        precip = 'null'
      snowfall = float(snow[yr-byear,mo,dy])
      if snowfall < 0 or snowfall > 150 or numpy.isnan(snowfall):
        snowfall = 'null'
      snowd = float(snwg[yr-byear,mo,dy])
      if snowd < 0 or snowd > 150 or numpy.isnan(snowd):
        snowd = 'null'
      if high == 'null' or low == 'null':
        continue

      sql = """INSERT into alldata_tmp(station, day, high, low, precip,
            snow, sday, year, month, snowd) VALUES ('IA8706', '%s-%s-%s',
            %s, %s, %s, %s, '%02i%02i', %s, %s, %s)""" % (yr,
            mo+1, dy+1, high, low, precip, snowfall, mo+1, dy+1, yr, mo+1,
            snowd)
      ccursor.execute(sql)


nc.close()
ccursor.close()
COOP.commit()
