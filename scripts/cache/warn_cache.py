# Need something to cache the warnings GIS files, since they are so 
# huge.

import os

FINAL = "/mesonet/share/pickup/wwa/"

for year in range(1986,2010):
  cmd = 'wget -q -O %s/%s_all.zip "http://localhost/cgi-bin/request/gis/watchwarn.py?year1=%s&month1=1&day1=1&hour1=0&minute1=0&year2=%s&month2=1&day2=1&hour2=0&minute2=0"' % (FINAL, year,  year, year+1)
  os.system(cmd)
  cmd = 'wget -q -O %s/%s_tsmf.zip "http://localhost/cgi-bin/request/gis/watchwarn.py?year1=%s&month1=1&day1=1&hour1=0&minute1=0&year2=%s&month2=1&day2=1&hour2=0&minute2=0&limite0=yes"'  % (FINAL, year,  year, year+1)
  os.system(cmd)
  if year > 2001:
    cmd = 'wget -q -O %s/%s_tsmf_sbw.zip "http://localhost/cgi-bin/request/gis/watchwarn.py?year1=%s&month1=1&day1=1&hour1=0&minute1=0&year2=%s&month2=1&day2=1&hour2=0&minute2=0&limit0=yes&limit1=yes"'  % (FINAL, year,  year, year+1)

    os.system(cmd)
