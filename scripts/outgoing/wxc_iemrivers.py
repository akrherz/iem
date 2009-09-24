
import re, os, shutil, mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

svr_dict = {"N": "None", "0": "Aerial", "1": "Minor", "2": "Moderate", "3": "Major", "U": "Unknown"}

o = open('wxc_iemrivers.txt', 'w')
o.write("""Weather Central 001d0300 Surface Data TimeStamp=%s
  10
   5 Station
  64 River Forecast Point
   7 Lat
   7 Lon
   7 Flood Stage
   7 Current Stage
   7 Forecast Stage
  12 Severity
  10 Trend
 128 Forecast Text
""" % (mx.DateTime.gmt().strftime("%Y.%m.%d.%H%M"), ) )

rs = postgis.query("select r.*, h.*, x(h.geom) as lon, y(h.geom) as lat \
   from hvtec_nwsli h, riverpro r,\
  (select distinct hvtec_nwsli from warnings_2008 WHERE \
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and \
   significance = 'W') as foo\
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli").dictresult()

for i in range(len(rs)):
  nwsli = rs[i]['nwsli']
  ft = re.findall("([0-9]+\.?[0-9]?)", rs[i]['flood_text'])
  if (len(ft) == 0):
    #print 'MISSING %s %s' % (nwsli, rs[i]['flood_text'])
    continue
  fstage = float(ft[-1])

  ft = re.findall("([0-9]+\.?[0-9]?)", rs[i]['stage_text'])
  if (len(ft) == 0):
    #print 'MISSING %s %s' % (nwsli, rs[i]['stage_text'])
    continue
  stage = float(ft[-1])

  forecast_text = rs[i]['forecast_text']
  trend = "Unknown"
  if (forecast_text.find("FALL ") > 0):
    trend = "Falling"
  if (forecast_text.find("RISING ") > 0):
    trend = "Rising"
  if (forecast_text.find("RISE ") > 0):
    trend = "Rising"
  ft = re.findall("([0-9]+\.?[0-9]?)", forecast_text)
  if (len(ft) == 0):
    ft = [0]
  xstage = float(ft[-1])

  severe = ""
  if (svr_dict.has_key(rs[i]['severity'])):
    severe = svr_dict[ rs[i]['severity'] ]

  rname = "%s %s %s" % (rs[i]['river_name'], rs[i]['proximity'],rs[i]['name'])
  ftxt = re.sub("\s+", " ", rs[i]['forecast_text'].strip() )
  o.write("%5s %-64.64s %7.2f %7.2f %7.2f %7.2f %7.2f %-12.12s %-10.10s %-128.128s\n" % \
     (rs[i]['nwsli'], rname, rs[i]['lat'], rs[i]['lon'], fstage, stage, \
      xstage, severe, trend, ftxt ))

o.close()

os.system("/home/ldm/bin/pqinsert wxc_iemrivers.txt")
shutil.copyfile("wxc_iemrivers.txt", "/mesonet/share/pickup/wxc/wxc_iemrivers.txt")
os.remove("wxc_iemrivers.txt")
