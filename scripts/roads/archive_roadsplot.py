"""Archive a road conditions plot every 5 minutes.

Called from RUN_5MIN.sh
"""
import datetime
import os
import sys
import subprocess
import tempfile

from pyiem.util import utc, logger
import pytz
import requests

LOG = logger()


def do(now):
    """Run for a given timestamp."""
    fn = now.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/iaroads/iaroads_%H%M.png"
    )
    if os.path.isfile(fn):
        LOG.debug("skipping as file %s exists", fn)
        return
    LOG.debug("running for %s", now)

    # CAREFUL, web takes valid in CST/CDT
    service = now.astimezone(pytz.timezone("America/Chicago")).strftime(
        "http://iem.local/roads/iem.php?valid=%Y-%m-%d%%20%H:%M"
    )
    routes = "ac" if (utc() - now) < datetime.timedelta(minutes=10) else "a"
    if routes == "ac":
        service = "http://iem.local/roads/iem.php"

    req = requests.get(service, timeout=60)
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(req.content)
    tmpfd.close()
    pqstr = "plot %s %s iaroads.png iaroads/iaroads_%s.png png" % (
        routes,
        now.strftime("%Y%m%d%H%M"),
        now.strftime("%H%M"),
    )
    LOG.debug(pqstr)
    subprocess.call("pqinsert -i -p '%s' %s" % (pqstr, tmpfd.name), shell=True)
    os.unlink(tmpfd.name)


def main(argv):
    """Go Main Go"""
    now = utc(*[int(i) for i in argv[1:6]])
    for offset in [0, 1440, 1440 + 720]:
        valid = now - datetime.timedelta(minutes=offset)
        do(valid)


if __name__ == "__main__":
    main(sys.argv)
