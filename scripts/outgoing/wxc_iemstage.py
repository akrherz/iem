"""
  Produce a WXC formatted file with stage information included! 
"""
import os
import subprocess
import shutil
import mx.DateTime
import iemdb
import psycopg2.extras
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)


o = open('wxc_iemstage.txt', 'w')
o.write("""Weather Central 001d0300 Surface Data TimeStamp=%s
  15
   5 Station
  64 Stage Location Name
   2 Day
   4 Hour
   7 Lat
   7 Lon
  10 Current Stage
  10 Sig Stage Low
  10 Sig Stage Action
  10 Sig Stage Bankfull
  10 Sig Stage Flood
  10 Sig Stage Moderate
  10 Sig Stage Major
  10 Sig Stage Record
  10 Sig Stage Text
""" % (mx.DateTime.gmt().strftime("%Y.%m.%d.%H%M"), ) )

def compute_text(row):
    """ Generate text of what this current stage is """
    stage = row['value']
    for s in ['Record', 'Major', 'Moderate', 'Flood', 'Bankfull', 'Action']:
        if row['ss_'+s.lower()] != 'M' and float(row['ss_'+s.lower()]) < stage:
            return s    
    return 'Normal'

icursor.execute("""
 SELECT c.value, x(geom) as lon, y(geom) as lat, name, station, valid,
 case when sigstage_low is null then 'M' else sigstage_low::text end as ss_low,
 case when sigstage_action is null then 'M' else sigstage_action::text end as ss_action,
 case when sigstage_bankfull is null then 'M' else sigstage_bankfull::text end as ss_bankfull,
 case when sigstage_flood is null then 'M' else sigstage_flood::text end as ss_flood,
 case when sigstage_moderate is null then 'M' else sigstage_moderate::text end as ss_moderate,
 case when sigstage_major is null then 'M' else sigstage_major::text end as ss_major,
 case when sigstage_record is null then 'M' else sigstage_record::text end as ss_record
from current_shef c JOIN stations s on (c.station = s.id) WHERE
 s.network in ('IA_DCP') and c.valid > now() - '4 hours'::interval
 and c.physical_code in ('HG','HP', 'HT') and c.duration = 'I' and c.extremum = 'Z'   
""" , () )

for row in icursor:
    nwsli = row['station']
    o.write("%5s %-64.64s %s %s %7.2f %7.2f %10.2f %10.10s %10.10s %10.10s %10.10s %10.10s %10.10s %10.10s %10.10s\n" % (
        row['station'], row['name'], row['valid'].day, row['valid'].strftime("%H%M"),
        row['lat'], row['lon'], row['value'],
        row['ss_low'],row['ss_action'],row['ss_bankfull'],row['ss_flood'],
        row['ss_moderate'],row['ss_major'],row['ss_record'],
        compute_text(row) ))

o.close()

subprocess.call("/home/ldm/bin/pqinsert wxc_iemstage.txt", shell=True)
shutil.copyfile("wxc_iemstage.txt", "/mesonet/share/pickup/wxc/wxc_iemstage.txt")
os.remove("wxc_iemstage.txt")