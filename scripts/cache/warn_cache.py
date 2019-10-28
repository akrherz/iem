"""Cache yearly warning shapefiles

Sadly, it takes the system 6-10 minutes to generate these online, so best to
pre-generate them and allow folks to download.

    This is a cron job from RUN_2AM.sh
"""
from __future__ import print_function
import datetime
import sys

import requests

FINAL = "/mesonet/share/pickup/wwa/"
URL = "http://iem.local/cgi-bin/request/gis/watchwarn.py"


def get_uri(uri, localfn):
    """Fetch the remote resource to a local file"""
    req = requests.get(uri)
    if req.status_code != 200:
        print(
            ("warn_cache[%s] failed with status: %s\n%s")
            % (req.status_code, uri, req.content)
        )
        return
    else:
        output = open(localfn, "wb")
        output.write(req.content)
        output.close()


def get_files(year):
    """Go get our files and then cache them! """
    myuri = (
        "%s?simple=yes&year1=%s&month1=1&day1=1&hour1=0&minute1=0"
        "&year2=%s&month2=12&day2=31&hour2=23&minute2=59"
    ) % (URL, year, year)
    get_uri(myuri, "%s/%s_all.zip" % (FINAL, year))

    # Now do SBW variant
    myuri = "%s&limit0=yes" % (myuri,)
    get_uri(myuri, "%s/%s_tsmf.zip" % (FINAL, year))

    if year > 2001:
        # Do SBW
        myuri = "%s&limit1=yes" % (myuri,)
        get_uri(myuri, "%s/%s_tsmf_sbw.zip" % (FINAL, year))


def main(argv):
    """Do Stuff"""
    # Lets go!
    if len(argv) == 2:
        get_files(int(argv[1]))
    else:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        get_files(yesterday.year)


if __name__ == "__main__":
    main(sys.argv)
