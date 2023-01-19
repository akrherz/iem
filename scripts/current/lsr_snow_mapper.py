"""Create an analysis of LSR snowfall reports"""
import tempfile
import os
import subprocess

import requests
from pyiem.util import (
    exponential_backoff,
    get_properties,
    get_dbconn,
    logger,
    utc,
)

LOG = logger()


def website_enable_check():
    """See if we should turn on the homepage graphic."""
    # See what our current status is
    status = get_properties().get("homepage.lsrmap.on") == "true"
    # See if we have any recent LSRs
    postgis = get_dbconn("postgis")
    cursor = postgis.cursor()
    cursor.execute(
        "SELECT valid from lsrs WHERE valid > now() - '12 hours'::interval "
        "and state = 'IA' and type = 'S'"
    )
    has_lsrs = cursor.rowcount > 0
    postgis.close()
    if status == has_lsrs:
        return
    LOG.warning("Setting homepage.lsrmap.on to %s", has_lsrs)
    mesosite = get_dbconn("mesosite")
    cursor = mesosite.cursor()
    cursor.execute(
        "UPDATE properties SET propvalue = %s where propname = %s",
        ("true" if has_lsrs else "false", "homepage.lsrmap.on"),
    )
    cursor.close()
    mesosite.commit()


def do(url, fn):
    """Do the work."""
    res = exponential_backoff(requests.get, url, timeout=60)
    if res is None:
        LOG.info("%s failure", url)
        return
    if res.status_code != 200:
        LOG.info("%s resulted in %s", url, res.status_code)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(res.content)
    pqstr = f"plot c {utc():%Y%m%d%H%M} {fn} bogus{utc().second} png"
    subprocess.call(["pqinsert", "-i", "-p", pqstr, tmpfd.name])
    os.unlink(tmpfd.name)


def main():
    """Go Main Go."""
    url = (
        "http://iem.local/plotting/auto/plot/207/t:state::csector:IA"
        "::p:both::hours:12::sz:25.png"
    )
    do(url, "lsr_snowfall.png")

    url = (
        "http://iem.local/plotting/auto/plot/207/t:state::csector:IA"
        "::p:contour::hours:12::sz:25.png"
    )
    do(url, "lsr_snowfall_nv.png")

    # -----------------
    url = (
        "http://iem.local/plotting/auto/plot/207/t:state::csector:midwest"
        "::p:contour::hours:12::sz:25.png"
    )
    do(url, "mw_lsr_snowfall.png")

    website_enable_check()


if __name__ == "__main__":
    main()
