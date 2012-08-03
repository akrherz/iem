
from Scientific.IO import NetCDF
import Numeric, mx.DateTime

dsm = NetCDF.NetCDFFile("/mesonet/xmclimate/DATA/O0CL_KDSM00000", 'r')
alo = NetCDF.NetCDFFile("/mesonet/xmclimate/DATA/O0CL_KALO00000", 'r')

dsm_mint = dsm.variables["mint"]
alo_mint = alo.variables["mint"]

print dsm.variables["byear"].getValue(), dsm.variables["bmonth"].getValue()
print alo.variables["byear"].getValue(), alo.variables["bmonth"].getValue()

for i in range(53,61):
  sts = mx.DateTime.DateTime(1944 + i, 1, 1)
  ets = sts + mx.DateTime.RelativeDateTime(years=+1)
  interval = mx.DateTime.RelativeDateTime(days=+1)
  now = sts
  while (now < ets):
    d = dsm_mint[i-1][now.month-1][now.day-1]
    l = alo_mint[i-6][now.month-1][now.day-1]
    if (d == 16384 or l == 16384):
      now += interval
      continue
    if (d - l >= 5):
      print "%s,%s,%s,%s" % (now.strftime("%Y-%m-%d"), d, l, d-l)
    now += interval
