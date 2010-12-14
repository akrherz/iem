"""
Dump out a file of the current RWIS traffic data for Iowa, please
"""

import iemdb
import os
import shutil
from psycopg2.extras import DictCursor
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor(cursor_factory=DictCursor)


out = open('wxc_iarwis_traffic.txt', 'w')
out.write("""Weather Central 001d0300 Surface Data
  12
   3 IEM Sensor ID
   5 Station ID
   7 Latitude
   9 Longitude
  32 Location Name
   2 Valid Day
   2 Valid Hour
   2 Valid Minute
   5 Average Speed MPH
   4 Normal Volume
   4 Long Axel Volume
   4 Occupancy
""")

icursor.execute("""SELECT r.*, l.nwsli, extract(hour from r.valid) as hour,
    extract(day from r.valid) as day, extract(minute from r.valid) as minute,
    (case when avg_speed is null then 0 else avg_speed end) as avgspeed,
    (case when long_vol is null then 0 else long_vol end) as longvol,
    (case when normal_vol is null then 0 else normal_vol end) as normalvol,
    (case when occupancy is null then 0 else occupancy end) as occ,
    x(s.geom) as lon, y(s.geom) as lat
    from rwis_traffic r, rwis_locations l, stations s
    WHERE s.id = l.nwsli and l.id = r.location_id and valid > (now() - '1 hour'::interval)
    ORDER by location_id, lane_id ASC""")
for row in icursor:
    out.write("%(id)3s %(nwsli)5.5s %(lat)7.4f %(lon)9.4f %(name)-32.32s %(day)2.0f %(hour)2.0f %(minute)2.0f %(avgspeed)5.1f %(normalvol)4.0f %(longvol)4.0f %(occ)4.0f\n" % row )

out.close()
os.system("/home/ldm/bin/pqinsert -p \"wxc_iarwis_traffic.txt\" wxc_iarwis_traffic.txt")
shutil.copyfile("wxc_iarwis_traffic.txt", "/mesonet/share/pickup/wxc/wxc_iarwis_traffic.txt")
os.remove("wxc_iarwis_traffic.txt")