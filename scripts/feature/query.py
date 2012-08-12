
import Nio

grib = Nio.open_file("gfs.t18z.pgrb2f78.grib2")

for v in grib.variables:
  print grib.variables[v]
sys.eixt()

print grib.variables['lv_ISBL0'][:]
sys.exit()
tmpk_2m = grib.variables['TMP_P0_L103_GLC0'][:]
lon  =  grib.variables["gridlon_0"][:]
lat  =  grib.variables["gridlat_0"][:]

val = Ngl.natgrid(lon, lat, tmpk_2m, [-93.,], [42.,])
print val
