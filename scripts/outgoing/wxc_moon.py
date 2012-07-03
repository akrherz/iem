"""
 Generate moon information for Iowa locations
"""

import ephem
import mx.DateTime
import os
import shutil
import network

nt = network.Table(("AWOS", "IA_ASOS"))

# P2 is yesterday
def figurePhase(p1,p2):
  if (p2 > p1):  # Waning!
    if (p1 < 0.1):
      return 'New Moon'
    if (p1 < 0.4):
      return 'Waning Crescent'
    if (p1 < 0.6):
      return 'Last Quarter'
    if (p1 < 0.9):
      return 'Waning_Gibbous'
    else:
      return 'Full Moon'
  else: # Waxing!
    if (p1 < 0.1):
      return 'New Moon'
    if (p1 < 0.4):
      return 'Waxing Crescent'
    if (p1 < 0.6):
      return 'First Quarter'
    if (p1 < 0.9):
      return 'Waxing_Gibbous'
    else:
      return 'Full Moon'

def mydate(d):
  if (d is None): return mx.DateTime.DateTime(1989,1,1)
  if (d == ""): return mx.DateTime.DateTime(1989,1,1)

  gts = mx.DateTime.strptime(str(d), '%Y/%m/%d %H:%M:%S')
  return gts.localtime()

m = ephem.Moon()

out = open('wxc_moon.txt', 'w')
out.write("""Weather Central 001d0300 Surface Data
   8
   4 Station
  30 Location
   6 Lat
   8 Lon
   8 MOON_RISE
   8 MOON_SET
  30 MOON_PHASE
   2 BOGUS
""")

for station in nt.sts.keys():
    ia = ephem.Observer()
    ia.lat = `nt.sts[station]['lat']`
    ia.long = `nt.sts[station]['lon']`
    ia.date = '%s 00:00' % (mx.DateTime.gmt().strftime("%Y/%m/%d"), )
    r1 = mydate(ia.next_rising(m))
    s1 = mydate(ia.next_setting(m))
    p1 = m.moon_phase

    ia.date = '%s 00:00' % ((mx.DateTime.gmt() - mx.DateTime.RelativeDateTime(days=1)).strftime("%Y/%m/%d"), )
    r2 = mydate(ia.next_rising(m))
    s2 = mydate(ia.next_setting(m))
    p2 = m.moon_phase

    mp = figurePhase(p1,p2)
    find_d = mx.DateTime.now().strftime("%Y%m%d")

    my_rise = r2
    if (r1.strftime("%Y%m%d") == find_d):
        my_rise = r1

    my_set = s2
    if (s1.strftime("%Y%m%d") == find_d):
        my_set = s1

    out.write("K%s %-30.30s %6.3f %8.3f %8s %8s %30s AA\n" % (station, 
                    nt.sts[station]['name'], nt.sts[station]['lat'], 
                    nt.sts[station]['lon'], my_rise.strftime("%-I:%M %P"), 
                    my_set.strftime("%-I:%M %P"), mp) )

out.close()

shutil.copyfile("wxc_moon.txt", "/mesonet/share/pickup/wxc/wxc_moon.txt")
os.system("/home/ldm/bin/pqinsert -p \"wxc_moon.txt\" wxc_moon.txt")
os.remove("wxc_moon.txt")
