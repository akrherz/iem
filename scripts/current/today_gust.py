"""Generate analysis of Peak Wind Gust."""
import datetime
import os
import subprocess
import tempfile

import requests


def main():
    """Go Main Go"""
    now = datetime.datetime.now()

    service = (
        "http://iem.local/plotting/auto/?_wait=no&q=206&t=state"
        "&state=IA&v=max_gust&p=both&day=%s&cmap=gist_stern&"
        "cmap_r=on&dpi=100&_fmt=png&_cb=1"
    ) % (now.strftime("%Y/%m/%d"),)

    req = requests.get(service, timeout=60)
    tmpfd = tempfile.NamedTemporaryFile(delete=False)
    tmpfd.write(req.content)
    tmpfd.close()

    pqstr = "plot ac %s summary/today_gust.png iowa_wind_gust.png png" % (
        now.strftime("%Y%m%d%H%M"),
    )
    subprocess.call(
        "/home/ldm/bin/pqinsert -i -p '%s' %s" % (pqstr, tmpfd.name),
        shell=True,
    )
    os.unlink(tmpfd.name)


if __name__ == "__main__":
    main()
