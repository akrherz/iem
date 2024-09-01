"""Cache yearly warning shapefiles

Sadly, it takes the system 6-10 minutes to generate these online, so best to
pre-generate them and allow folks to download.

This is a cron job from RUN_2AM.sh
"""

import click
import httpx
from pyiem.util import logger, utc

LOG = logger()
FINAL = "/mesonet/share/pickup/wwa/"
URL = "http://iem.local/cgi-bin/request/gis/watchwarn.py"


def get_uri(uri, localfn):
    """Fetch the remote resource to a local file"""
    req = httpx.get(uri, timeout=1200)
    if req.status_code != 200:
        LOG.warning(
            "warn_cache[%s] failed with status: %s\n%s",
            req.status_code,
            uri,
            req.content,
        )
        return
    with open(localfn, "wb") as fh:
        fh.write(req.content)


def get_files(year):
    """Go get our files and then cache them!"""
    myuri = (
        f"{URL}?simple=yes&year1={year}&month1=1&day1=1&hour1=0&minute1=0"
        f"&year2={year}&month2=12&day2=31&hour2=23&minute2=59"
    )
    get_uri(myuri, f"{FINAL}/{year}_all.zip")

    # Now do SBW variant
    myuri = f"{myuri}&limit0=yes"
    get_uri(myuri, f"{FINAL}/{year}_tsmf.zip")

    if year > 2001:
        # Do SBW
        myuri = f"{myuri}&limit1=yes"
        get_uri(myuri, f"{FINAL}/{year}_tsmf_sbw.zip")


@click.command()
@click.option("--year", default=utc().year, type=int, help="Year to process")
def main(year: int):
    """Do Stuff"""
    get_files(year)


if __name__ == "__main__":
    main()
