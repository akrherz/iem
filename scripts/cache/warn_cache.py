"""Cache yearly warning shapefiles

Sadly, it takes the system 6-10 minutes to generate these online, so best to
pre-generate them and allow folks to download.

    This is a cron job from RUN_2AM.sh
"""
import requests
import datetime
import sys

FINAL = "/mesonet/share/pickup/wwa/"
URL = "http://iem.local/cgi-bin/request/gis/watchwarn.py"


def get_files(year):
    """Go get our files and then cache them! """
    myuri = ('%s?simple=yes&year1=%s&month1=1&day1=1&hour1=0&minute1=0'
             '&year2=%s&month2=12&day2=31&hour2=23&minute2=59'
             ) % (URL, year, year)

    req = requests.get(myuri)
    if req.status_code != 200:
        print("warn_cache[%s] failed with status: %s\n%s" % (req.status, myuri)
              )
        return
    else:
        o = open("%s/%s_all.zip" % (FINAL, year), 'wb')
        o.write(req.content)
        o.close()

    # Now do SBW variant
    myuri = "%s&limit0=yes" % (myuri,)
    req = requests.get(myuri)
    if req.status_code != 200:
        print("warn_cache[%s] failed with status: %s\n%s" % (req.status, myuri)
              )
    else:
        o = open("%s/%s_tsmf.zip" % (FINAL, year), 'wb')
        o.write(req.content)
        o.close()

    if year > 2001:
        # Do SBW
        myuri = "%s&limit1=yes" % (myuri,)
        req = requests.get(myuri)
        if req.status_code != 200:
            print(("warn_cache[%s] failed with status: %s\n%s"
                   ) % (req.status, myuri))
        else:
            o = open("%s/%s_tsmf_sbw.zip" % (FINAL, year), 'wb')
            o.write(req.content)
            o.close()

if __name__ == "__main__":
    # Lets go!
    if len(sys.argv) == 2:
        get_files(sys.argv[1])
    else:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        get_files(yesterday.year)
