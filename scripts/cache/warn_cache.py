# Need something to cache the warnings GIS files, since they are so 
# huge.

import os
import mx.DateTime

FINAL = "/mesonet/share/pickup/wwa/"
URL = "http://iem21.local/cgi-bin/request/gis/watchwarn.py"


def get_files(sts, ets):
    year = mx.DateTime.now().year
    cmd = 'wget --timeout=60000 -q -O %s/%s_all.zip "%s?year1=%s&month1=1&day1=1&hour1=0&minute1=0&year2=%s&month2=%s&day2=%s&hour2=0&minute2=0"' % (FINAL, 
                            sts.year,  URL, sts.year, ets.year, ets.month, ets.day)
    os.system(cmd)
    cmd = 'wget --timeout=60000 -q -O %s/%s_tsmf.zip "%s?year1=%s&month1=1&day1=1&hour1=0&minute1=0&year2=%s&month2=%s&day2=%s&hour2=0&minute2=0&limit0=yes"'  % (FINAL, 
                            sts.year,  URL, sts.year, ets.year, ets.month, ets.day)
    os.system(cmd)
    if year > 2001:
        cmd = 'wget --timeout=60000 -q -O %s/%s_tsmf_sbw.zip "%s?year1=%s&month1=1&day1=1&hour1=0&minute1=0&year2=%s&month2=%s&day2=%s&hour2=0&minute2=0&limit0=yes&limit1=yes"'  % (FINAL, 
                 sts.year,  URL, sts.year, ets.year, ets.month, ets.day)
        os.system(cmd)
        

if __name__ == "__main__":
    sts = mx.DateTime.now() + mx.DateTime.RelativeDateTime(day=1,month=1,hour=0,minute=0)
    ets = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=1,hour=0,minute=0)
    get_files(sts, ets)
