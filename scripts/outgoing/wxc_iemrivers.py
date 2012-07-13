"""
Generate a Weather Central Formatted data file with HVTEC River information
in it!
"""
import re
import os
import subprocess
import shutil
import mx.DateTime
import iemdb
import psycopg2.extras
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)

svr_dict = {"N": "None", "0": "Aerial", "1": "Minor", "2": "Moderate", 
            "3": "Major", "U": "Unknown"}

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

pcursor.execute("""select r.*, h.*, x(h.geom) as lon, y(h.geom) as lat 
   from hvtec_nwsli h, riverpro r,
  (select distinct hvtec_nwsli from warnings_%s WHERE 
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and 
   significance = 'W') as foo
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli""" % (
   mx.DateTime.now().year,) )

for row in pcursor:
    nwsli = row['nwsli']
    ft = re.findall("([0-9]+\.?[0-9]?)", row['flood_text'])
    if len(ft) == 0:
        #print 'MISSING %s %s' % (nwsli, rs[i]['flood_text'])
        continue
    fstage = float(ft[-1])

    ft = re.findall("([0-9]+\.?[0-9]?)", row['stage_text'])
    if len(ft) == 0:
        #print 'MISSING %s %s' % (nwsli, rs[i]['stage_text'])
        continue
    stage = float(ft[-1])
    if svr_dict.has_key(row['severity']):
        severe = svr_dict[ row['severity'] ]

    forecast_text = row['forecast_text']
    trend = "Unknown"
    if forecast_text.find("FALL ") > 0:
        trend = "Falling"
    if forecast_text.find("RISING ") > 0:
        trend = "Rising"
    if forecast_text.find("RISE ") > 0:
        trend = "Rising"
    ft = re.findall("([0-9]+\.?[0-9]?)", forecast_text)
    if len(ft) == 0:
        ft = [0]
    xstage = float(ft[-1])

    severe = svr_dict.get(row['severity'], "")

    rname = "%s %s %s" % (row['river_name'], row['proximity'], row['name'])
    ftxt = re.sub("\s+", " ", row['forecast_text'].strip() )
    o.write("%5s %-64.64s %7.2f %7.2f %7.2f %7.2f %7.2f %-12.12s %-10.10s %-128.128s\n" % (
        row['nwsli'], rname, row['lat'], row['lon'], fstage, stage, 
      xstage, severe, trend, ftxt ))

o.close()

subprocess.call("/home/ldm/bin/pqinsert wxc_iemrivers.txt", shell=True)
shutil.copyfile("wxc_iemrivers.txt", "/mesonet/share/pickup/wxc/wxc_iemrivers.txt")
os.remove("wxc_iemrivers.txt")
