'''
 Lets build a cache of warning files so to allow easier download
 - run from RUN_2AM.sh
'''

import subprocess
import datetime
import sys
import shutil

FINAL = "/mesonet/share/pickup/wwa/"
URL = "http://iem.local/cgi-bin/request/gis/watchwarn.py"


def get_files(year):
    ''' Go get our files and then cache them! '''
    common = 'simple=yes&year1=%s&month1=1&day1=1&hour1=0&minute1=0' % (year,)
    common += '&year2=%s&month2=12&day2=31&hour2=23&minute2=59' % (year,)

    cmd = 'wget --timeout=60000 -q -O /tmp/%s_all.zip "%s?%s"' % (year,
                                                                  URL, common)
    subprocess.call(cmd, shell=True)
    shutil.move("/tmp/%s_all.zip" % (year,),
                "%s/%s_all.zip" % (FINAL, year))

    cmd = 'wget --timeout=60000 -q -O /tmp/%s_tsmf.zip "%s?%s&limit0=yes"' % (
                            year, URL, common)
    subprocess.call(cmd, shell=True)
    shutil.move("/tmp/%s_tsmf.zip" % (year,),
                "%s/%s_tsmf.zip" % (FINAL, year))

    if year > 2001:
        cmd = ('wget --timeout=60000 -q -O /tmp/%s_tsmf_sbw.zip'
               ' "%s?%s&limit0=yes&limit1=yes"') % (year,  URL, common)
        subprocess.call(cmd, shell=True)
        shutil.move("/tmp/%s_tsmf_sbw.zip" % (year,),
                    "%s/%s_tsmf_sbw.zip" % (FINAL, year))


if __name__ == "__main__":
    # Lets go!
    if len(sys.argv) == 2:
        get_files(sys.argv[1])
    else:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        get_files(yesterday.year)
