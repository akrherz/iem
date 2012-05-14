import netCDF3
import iemdb
COOP = iemdb.connect('coop')
ccursor = COOP.cursor()

nc = netCDF3.Dataset('DSM.nc')

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
      high = float(maxt[yr-byear,mo,dy]) / 1.0
      if high < -100 or high > 150:
        high = 'null'
      low = float(mint[yr-byear,mo,dy])  / 1.0
      if low < -100 or low > 150:
        low = 'null'
      precip = float(pcpn[yr-byear,mo,dy]) / 100.0
      if precip < -100 or precip > 150:
        precip = 'null'
      snowfall = float(snow[yr-byear,mo,dy]) / 10.0
      if snowfall < -100 or snowfall > 150:
        snowfall = 'null'
      snowd = float(snwg[yr-byear,mo,dy]) / 1.0
      if snowd < -100 or snowd > 150:
        snowd = 'null'
      if high == 'null' or low == 'null':
        continue

      sql = """INSERT into alldata_tmp(station, day, high, low, precip,
            snow, sday, year, month, snowd) VALUES ('IA2203', '%s-%s-%s',
            %s, %s, %s, %s, '%02i%02i', %s, %s, %s)""" % (yr,
            mo+1, dy+1, high, low, precip, snowfall, mo+1, dy+1, yr, mo+1,
            snowd)
      ccursor.execute(sql)


nc.close()
ccursor.close()
COOP.commit()
