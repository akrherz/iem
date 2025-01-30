"""Create an analysis of LSR snowfall reports"""

import os
import subprocess
import tempfile

import httpx
from pyiem.database import get_dbconn
from pyiem.util import (
    get_properties,
    logger,
    set_property,
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
    cursor.close()
    postgis.close()
    if status == has_lsrs:
        return
    LOG.warning("Setting homepage.lsrmap.on to %s", has_lsrs)
    set_property("homepage.lsrmap.on", "true" if has_lsrs else "false")


def do(url, fn):
    """Do the work."""
    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as exp:
        LOG.info("failure %s for %s", exp, url)
        return
    with tempfile.NamedTemporaryFile(delete=False) as tmpfd:
        tmpfd.write(resp.content)
    pqstr = f"plot c {utc():%Y%m%d%H%M} {fn} bogus{utc().second} png"
    subprocess.call(["pqinsert", "-i", "-p", pqstr, tmpfd.name])
    os.unlink(tmpfd.name)


def main():
    """Go Main Go."""
    ap207 = "http://iem.local/plotting/auto/plot/207"
    url = f"{ap207}/t:state::csector:IA::p:both::hours:12::sz:25.png"
    do(url, "lsr_snowfall.png")

    url = f"{ap207}/t:state::csector:IA::p:contour::hours:12::sz:25.png"
    do(url, "lsr_snowfall_nv.png")

    # -----------------
    url = f"{ap207}/t:state::csector:midwest::p:contour::hours:12::sz:25.png"
    do(url, "mw_lsr_snowfall.png")

    website_enable_check()


if __name__ == "__main__":
    main()
